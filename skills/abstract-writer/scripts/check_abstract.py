#!/usr/bin/env python3
"""Check a patent abstract against CN character and EN word limits.

Counting rules
    Chinese (审查指南: 摘要文字部分包括标点符号，不得超过300个字):
        COUNTING_RULE_ZH — every character counts, including punctuation;
        whitespace is excluded (space, tab, newline, and fullwidth space U+3000).
    English (37 CFR 1.72(b) preferably not exceeding 150 words; PCT Rule 8 prefers 50 to 150):
        COUNTING_RULE_EN — whitespace-separated tokens. A hyphenated compound
        is one word. This checker fails a draft longer than 150 words.

Warnings (exit 2, or exit 1 when the length limit is also exceeded)
    Claim-like phrasing: 其特征在于 / 其特征是 / "characterized in that".
    Advertising or puffery (商业性宣传用语), including 最佳, 革命性, revolutionary, unique.

Exit codes
    0  within limit and no warnings
    1  over the length limit
    2  within limit, with warnings
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

COUNTING_RULE_ZH = (
    "Chinese abstract length counts every character, including punctuation, "
    "and excludes whitespace (space, tab, newline, and fullwidth space U+3000). "
    "The limit is 300 characters, following the Guidelines for Patent Examination "
    "rule that the text of the abstract, punctuation included, must not exceed 300 characters."
)

COUNTING_RULE_EN = (
    "English abstract length counts whitespace-separated tokens. "
    "A hyphenated compound is one word. 37 CFR 1.72(b) says the abstract "
    "should be as concise as the disclosure permits, preferably not exceeding "
    "150 words. This checker fails a draft longer than 150 words. "
    "PCT Rule 8 prefers 50 to 150 words when the abstract is in English."
)

CN_CLAIM_PHRASES = ["其特征在于", "其特征是"]
EN_CLAIM_PHRASES = ["characterized in that", "characterised in that"]

CN_ADVERTISING = [
    "无与伦比",
    "国际领先",
    "填补空白",
    "世界第一",
    "革命性",
    "最佳",
    "最好",
    "完美",
    "独特",
    "领先",
    "卓越",
    "唯一",
]

EN_ADVERTISING = [
    "world-leading",
    "cutting-edge",
    "first-class",
    "unparalleled",
    "revolutionary",
    "superior",
    "perfect",
    "unique",
    "best",
]


def detect_lang(text: str) -> str:
    cjk = len(re.findall(r"[\u4e00-\u9fff]", text))
    latin = len(re.findall(r"[A-Za-z]", text))
    return "zh" if cjk > latin else "en"


def count_zh(text: str) -> int:
    return len(re.sub(r"\s+", "", text))


def count_en(text: str) -> int:
    return len(re.findall(r"\S+", text))


def _warnings(text: str, lang: str) -> list[dict]:
    found: list[dict] = []
    seen: set[tuple[str, str]] = set()

    def add(code: str, phrase: str, message: str) -> None:
        key = (code, phrase)
        if key in seen:
            return
        seen.add(key)
        found.append({"code": code, "phrase": phrase, "message": message})

    if lang == "zh":
        for phrase in CN_CLAIM_PHRASES:
            if phrase in text:
                add(
                    "claim_language",
                    phrase,
                    f"Abstract contains claim-like wording '{phrase}'. State the technical point in plain sentences.",
                )
        for phrase in CN_ADVERTISING:
            if phrase in text:
                add(
                    "advertising_language",
                    phrase,
                    f"Abstract contains advertising or puffery '{phrase}' (商业性宣传用语).",
                )
    else:
        lowered = text.lower()
        for phrase in EN_CLAIM_PHRASES:
            if phrase in lowered:
                add(
                    "claim_language",
                    phrase,
                    "Abstract contains claim-like wording 'characterized in that'.",
                )
        for phrase in EN_ADVERTISING:
            if "-" in phrase:
                if phrase in lowered:
                    add(
                        "advertising_language",
                        phrase,
                        f"Abstract contains advertising or puffery '{phrase}'.",
                    )
            elif re.search(rf"\b{re.escape(phrase)}\b", lowered):
                add(
                    "advertising_language",
                    phrase,
                    f"Abstract contains advertising or puffery '{phrase}'.",
                )
    return found


def analyze_text(text: str, lang: str = "auto", filename: str | None = None) -> dict:
    chosen = detect_lang(text) if lang == "auto" else lang
    if chosen == "zh":
        count = count_zh(text)
        limit = 300
        unit = "characters"
        rule = COUNTING_RULE_ZH
    else:
        count = count_en(text)
        limit = 150
        unit = "words"
        rule = COUNTING_RULE_EN
    warnings = _warnings(text, chosen)
    errors = []
    over = count > limit
    if over:
        errors.append(
            {
                "code": "over_limit",
                "count": count,
                "limit": limit,
                "message": f"Abstract is {count} {unit}; the limit is {limit}.",
            }
        )
    return {
        "file": filename,
        "lang": chosen,
        "count": count,
        "limit": limit,
        "unit": unit,
        "counting_rule": rule,
        "over_limit": over,
        "warnings": warnings,
        "errors": errors,
    }


def analyze_path(path: Path | str, lang: str = "auto") -> dict:
    file_path = Path(path)
    text = file_path.read_text(encoding="utf-8-sig")
    return analyze_text(text, lang=lang, filename=str(file_path))


def exit_code(report: dict) -> int:
    if report["errors"]:
        return 1
    if report["warnings"]:
        return 2
    return 0


def render_text(report: dict) -> str:
    lines = [
        "Abstract length report",
        f"File: {report.get('file') or '(text)'}",
        f"Language: {report['lang']}",
        f"Count: {report['count']} {report['unit']} (limit {report['limit']})",
        f"Counting rule: {report['counting_rule']}",
        "",
    ]
    if report["errors"]:
        lines.append("ERRORS")
        for error in report["errors"]:
            lines.append(f"- [{error['code']}] {error['message']}")
    if report["warnings"]:
        lines.append("WARNINGS")
        for warning in report["warnings"]:
            lines.append(f"- [{warning['code']}] {warning['message']}")
    if not report["errors"] and not report["warnings"]:
        lines.append("Result: PASS")
    elif report["errors"]:
        lines.append("Result: FAIL")
    else:
        lines.append("Result: PASS WITH WARNINGS")
    return "\n".join(lines)


def emit(report: dict, fmt: str) -> None:
    if fmt in ("text", "both"):
        print(render_text(report))
    if fmt == "both":
        print("===JSON===")
    if fmt in ("json", "both"):
        print(json.dumps(report, ensure_ascii=False, indent=2))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check CN/US/PCT abstract length and wording.")
    parser.add_argument("abstract", type=Path, help="Abstract markdown file")
    parser.add_argument("--lang", choices=["zh", "en", "auto"], default="auto")
    parser.add_argument("--format", choices=["text", "json", "both"], default="both")
    args = parser.parse_args(argv)
    if not args.abstract.is_file():
        print(f"File not found: {args.abstract}", file=sys.stderr)
        return 2
    report = analyze_path(args.abstract, lang=args.lang)
    emit(report, args.format)
    return exit_code(report)


if __name__ == "__main__":
    sys.exit(main())
