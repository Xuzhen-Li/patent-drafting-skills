#!/usr/bin/env python3
"""Compare reference numerals in a description with a drawings manifest.

Manifest
    {
      "figures": [
        {"id": "FIG. 1", "numerals": {"10": "housing", "12": "sensor"}}
      ]
    }
    Chinese figure ids such as "图1" are accepted. Numeral keys are strings
    of digits. Names should use the same noun the description uses.

Text patterns
    English: "housing 10", "control module 14", "housing (10)"
    Chinese: "壳体10", "壳体(10)", "壳体（10）"

Reported defects
    numeral_missing_in_text        in the manifest, absent from the text
    numeral_missing_in_drawings    in the text, absent from the manifest
    numeral_multiple_names         one numeral has two or more names
    name_multiple_numerals         one name has two or more numerals

Names are compared exactly after light cleanup (case-folding for Latin text,
stripping leading 包括/所述/与). "金属壳体" and "壳体" are different names.
Numbers of 4 digits that are not in the manifest are ignored (years).
Figure labels (FIG. 1 / 图1) and quantities such as "3个" are not part names.

Exit codes
    0  no defects
    1  one or more defects
    2  missing file or invalid JSON
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

CN_PREFIXES = [
    "设置在",
    "安装在",
    "连接于",
    "连接在",
    "固定在",
    "位于",
    "包括",
    "具有",
    "设有",
    "含有",
    "所述",
    "一个",
    "一种",
]

EN_LEADING = {
    "the", "a", "an", "said", "of", "and", "or", "with", "for", "to", "from",
    "by", "in", "on", "at", "into", "onto", "within", "inside", "its", "contains",
    "encloses", "includes", "including", "having", "wherein", "is", "are",
    "mounted", "shows", "show",
}

EN_REJECT = {
    "figure", "fig", "figs", "table", "claim", "claims", "section", "paragraph",
    "step", "example", "embodiment", "page", "in", "on", "at", "of", "and",
}

EN_PAIR = re.compile(
    r"(?P<name>(?:[A-Za-z][A-Za-z0-9-]*\s+){0,3}[A-Za-z][A-Za-z0-9-]*)"
    r"\s*(?:[（(]\s*(?P<n1>\d{1,4})\s*[)）]|(?P<n2>\d{1,4}))(?!\d)"
)

CN_PAREN = re.compile(r"([\u4e00-\u9fff]{1,12})[（(]\s*(\d{1,4})\s*[)）]")
CN_ADJACENT = re.compile(r"([\u4e00-\u9fff]{1,12})(\d{1,4})(?!\d)")

CN_UNITS = set("个种次条项倍年月日号%％度")

LIMITATIONS = [
    "The numeral must follow the name ('housing 10', '壳体10', '壳体(10)'). '10 housing' is not read.",
    "Chinese names are the characters immediately before the numeral, with a short list of prefixes removed (包括, 所述, 与). Extra modifiers stay in the name, so 金属壳体 and 壳体 do not match.",
    "English names keep up to four words and drop leading articles. Comparison is case-insensitive and exact after that cleanup.",
    "Figure captions (FIG. 1, 图1), claim numbers, and Chinese quantities ending in 个/种/次/条/项 are skipped.",
    "Four-digit numbers that are not keys in the manifest are ignored so years are less likely to be treated as reference signs.",
]


def tidy_cn(run: str) -> str:
    run = run.strip()
    changed = True
    while changed and run:
        changed = False
        stripped = re.sub(r"^[和与及、，,的]+", "", run)
        if stripped != run:
            run = stripped
            changed = True
        for prefix in sorted(CN_PREFIXES, key=len, reverse=True):
            if run.startswith(prefix) and len(run) > len(prefix):
                run = run[len(prefix) :]
                changed = True
                break
    if not run or run.endswith("图") or "实施例" in run or run.endswith("步骤"):
        return ""
    return run


def tidy_en(name: str) -> str:
    """Keep the noun after the last article.

    'contacts the housing' -> housing. 'the control module' -> control module.
    A name with no article is kept as written, up to four words.
    """
    words = name.split()
    articles = {"the", "a", "an", "said"}
    last_article = None
    for index, word in enumerate(words):
        if word.lower() in articles:
            last_article = index
    if last_article is not None:
        words = words[last_article + 1 :]
    while words and words[0].lower() in EN_LEADING:
        words.pop(0)
    while words and words[-1].lower() in EN_LEADING:
        words.pop()
    if not words:
        return ""
    words = words[-4:]
    if any(word.lower() in {"figure", "fig", "figs"} for word in words):
        return ""
    if len(words) == 1 and words[0].lower() in EN_REJECT:
        return ""
    return " ".join(word.lower() for word in words)


def norm_name(name: str) -> str:
    name = re.sub(r"\s+", " ", name.strip())
    if re.search(r"[A-Za-z]", name):
        name = name.lower()
    return name


def extract_pairs(text: str) -> list[tuple[str, str]]:
    """Return (numeral, name) pairs in reading order, without duplicates."""
    found: list[tuple[str, str]] = []
    seen: set[tuple[str, str]] = set()

    def add(numeral: str, name: str) -> None:
        if not numeral or not name:
            return
        key = (numeral, name)
        if key in seen:
            return
        seen.add(key)
        found.append(key)

    for match in CN_PAREN.finditer(text):
        add(match.group(2), tidy_cn(match.group(1)))
    for match in CN_ADJACENT.finditer(text):
        end = match.end()
        if end < len(text) and text[end] in CN_UNITS:
            continue
        add(match.group(2), tidy_cn(match.group(1)))
    for match in EN_PAIR.finditer(text):
        numeral = match.group("n1") or match.group("n2")
        add(numeral, tidy_en(match.group("name")))
    return found


def _sort_num(numeral: str) -> tuple:
    return (0, int(numeral)) if numeral.isdigit() else (1, numeral)


def analyze(text: str, manifest: dict) -> dict:
    if not isinstance(manifest, dict):
        raise ValueError("manifest must be a JSON object")
    figures = manifest.get("figures") or []
    draw_names: dict[str, set[str]] = defaultdict(set)
    draw_figs: dict[str, set[str]] = defaultdict(set)
    for figure in figures:
        if not isinstance(figure, dict):
            continue
        fig_id = str(figure.get("id") or "")
        numerals = figure.get("numerals") or {}
        if not isinstance(numerals, dict):
            continue
        for raw_num, raw_name in numerals.items():
            numeral = str(raw_num).strip()
            name = norm_name(str(raw_name))
            if not numeral or not name:
                continue
            draw_names[numeral].add(name)
            if fig_id:
                draw_figs[numeral].add(fig_id)

    manifest_nums = set(draw_names)
    text_names: dict[str, set[str]] = defaultdict(set)
    pairs = []
    for numeral, name in extract_pairs(text):
        if len(numeral) >= 4 and numeral not in manifest_nums:
            continue
        cleaned = norm_name(name)
        if not cleaned:
            continue
        text_names[numeral].add(cleaned)
        pairs.append({"numeral": numeral, "name": cleaned})

    errors = []
    for numeral in sorted(draw_names, key=_sort_num):
        if numeral not in text_names:
            names = sorted(draw_names[numeral])
            errors.append(
                {
                    "code": "numeral_missing_in_text",
                    "numeral": numeral,
                    "names": names,
                    "figures": sorted(draw_figs[numeral]),
                    "message": (
                        f"Numeral {numeral} ({', '.join(names)}) is in the drawings "
                        "but not in the description."
                    ),
                }
            )
    for numeral in sorted(text_names, key=_sort_num):
        if numeral not in draw_names:
            names = sorted(text_names[numeral])
            errors.append(
                {
                    "code": "numeral_missing_in_drawings",
                    "numeral": numeral,
                    "names": names,
                    "message": (
                        f"Numeral {numeral} ({', '.join(names)}) is in the description "
                        "but not in the drawings manifest."
                    ),
                }
            )

    for numeral in sorted(set(draw_names) | set(text_names), key=_sort_num):
        names = draw_names[numeral] | text_names[numeral]
        if len(names) >= 2:
            errors.append(
                {
                    "code": "numeral_multiple_names",
                    "numeral": numeral,
                    "names": sorted(names),
                    "message": f"Numeral {numeral} is used for more than one name: {', '.join(sorted(names))}.",
                }
            )

    name_to_nums: dict[str, set[str]] = defaultdict(set)
    for numeral, names in list(draw_names.items()) + list(text_names.items()):
        for name in names:
            name_to_nums[name].add(numeral)
    for name in sorted(name_to_nums):
        nums = name_to_nums[name]
        if len(nums) >= 2:
            ordered = sorted(nums, key=_sort_num)
            errors.append(
                {
                    "code": "name_multiple_numerals",
                    "name": name,
                    "numerals": ordered,
                    "message": f"Name '{name}' is used with more than one numeral: {', '.join(ordered)}.",
                }
            )

    return {
        "errors": errors,
        "error_count": len(errors),
        "pairs": pairs,
        "limitations": list(LIMITATIONS),
    }


def render_text(report: dict) -> str:
    lines = ["Reference numeral report", ""]
    if not report["errors"]:
        lines.append("Result: PASS")
    else:
        lines.append(f"ERRORS ({report['error_count']})")
        for error in report["errors"]:
            lines.append(f"- [{error['code']}] {error['message']}")
        lines.append("")
        lines.append("Result: FAIL")
    lines.append("")
    lines.append("Heuristic limitations:")
    for item in report.get("limitations", []):
        lines.append(f"- {item}")
    return "\n".join(lines)


def emit(report: dict, fmt: str) -> None:
    if fmt in ("text", "both"):
        print(render_text(report))
    if fmt == "both":
        print("===JSON===")
    if fmt in ("json", "both"):
        print(json.dumps(report, ensure_ascii=False, indent=2))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Match description numerals to a drawings manifest.")
    parser.add_argument("description", type=Path, help="description.md")
    parser.add_argument("manifest", type=Path, help="drawings manifest JSON")
    parser.add_argument("--format", choices=["text", "json", "both"], default="both")
    args = parser.parse_args(argv)
    if not args.description.is_file():
        print(f"File not found: {args.description}", file=sys.stderr)
        return 2
    if not args.manifest.is_file():
        print(f"File not found: {args.manifest}", file=sys.stderr)
        return 2
    try:
        manifest = json.loads(args.manifest.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as exc:
        print(f"Invalid manifest JSON: {exc}", file=sys.stderr)
        return 2
    text = args.description.read_text(encoding="utf-8-sig")
    try:
        report = analyze(text, manifest)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    emit(report, args.format)
    return 1 if report["errors"] else 0


if __name__ == "__main__":
    sys.exit(main())
