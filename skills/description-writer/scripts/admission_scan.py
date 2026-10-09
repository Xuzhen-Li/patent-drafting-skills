#!/usr/bin/env python3
"""Flag background sentences that treat the invention as already known.

The scan looks at the background section only. A sentence is flagged when it
uses a "known" marker and either calls the present invention already known,
or gives no citation the reader can open.

This is a drafting flag, not a legal conclusion.

    admission_scan.py <description.md>

Exit codes
    0  no flags
    1  one or more flags
    2  file missing
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

CN_MARKERS = ("众所周知", "公知", "已为公众所知", "现有技术已经", "本发明已被", "本发明是已知", "本发明的方案已被")
EN_MARKERS = (
    "well known",
    "already known",
    "it is known",
    "the present invention is known",
    "the present invention has been",
    "our solution is known",
    "conventional in the art",
)
INVENTION_ATTR = re.compile(r"本发明|the present invention|our solution", re.IGNORECASE)
CITATION = re.compile(
    r"(CN|US|EP|WO|JP)\s?\d|\bhttps?://|见检索|search log|\bD\d+\b",
    re.IGNORECASE,
)
HEADING = re.compile(r"^#{1,6}\s*(.+?)\s*$")
NEXT_SECTION = re.compile(
    r"^(发明内容|附图说明|具体实施方式|disclosure of the invention|brief summary|"
    r"brief description of the drawings|detailed description|summary)\b",
    re.IGNORECASE,
)
BACKGROUND = re.compile(r"^(背景技术|background(\s+art)?|background of the invention)\b", re.IGNORECASE)


def background_lines(text: str) -> list[tuple[int, str]]:
    lines = text.splitlines()
    start = None
    for index, line in enumerate(lines):
        heading = HEADING.match(line.strip())
        title = heading.group(1) if heading else line.strip()
        if start is None and BACKGROUND.match(title):
            start = index + 1
            continue
        if start is not None and (HEADING.match(line.strip()) or NEXT_SECTION.match(title)):
            if BACKGROUND.match(title):
                continue
            return [(number, lines[number - 1]) for number in range(start + 1, index + 1)]
    if start is None:
        return []
    return [(number, lines[number - 1]) for number in range(start + 1, len(lines) + 1)]


def scan(text: str) -> dict:
    flags = []
    for number, raw in background_lines(text):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        lowered = line.lower()
        if not any(marker in line for marker in CN_MARKERS) and not any(marker in lowered for marker in EN_MARKERS):
            continue
        reasons = []
        if INVENTION_ATTR.search(line):
            reasons.append("attributes_the_invention_to_the_prior_art")
        if not CITATION.search(line):
            reasons.append("known_without_source")
        if reasons:
            flags.append({"line": number, "text": line, "reasons": reasons})
    return {"flags": flags, "flag_count": len(flags), "result": "PASS" if not flags else "FAIL"}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Flag background admissions that the invention is already known.")
    parser.add_argument("description", type=Path)
    args = parser.parse_args(argv)
    if not args.description.is_file():
        print(f"File not found: {args.description}", file=sys.stderr)
        return 2
    report = scan(args.description.read_text(encoding="utf-8-sig"))
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if report["flags"] else 0


if __name__ == "__main__":
    sys.exit(main())
