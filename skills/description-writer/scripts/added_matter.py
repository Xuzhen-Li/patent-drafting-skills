#!/usr/bin/env python3
"""Mark description sentences that are not in the locked disclosure.

A sentence is treated as already disclosed when its wording is in the
disclosure, when most of its Chinese character pairs are, or when most of
its English content words are. A number that never appears in the disclosure
is marked even if the surrounding words overlap.

Headings and the unconfirmed marker are not sentences of technical matter.
The list is a warning for counsel. It does not delete text.

    added_matter.py <description.md> <disclosure.md>

Exit codes
    0  no unmarked sentences
    1  one or more sentences are not in the disclosure
    2  a file is missing
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

HEADINGS = {
    "技术领域",
    "背景技术",
    "发明内容",
    "附图说明",
    "具体实施方式",
    "technical field",
    "background",
    "background art",
    "brief summary",
    "brief description of the drawings",
    "detailed description",
    "summary",
    "industrial applicability",
}
EN_STOP = {
    "the", "and", "for", "with", "that", "this", "from", "into", "onto", "are",
    "was", "were", "has", "have", "been", "being", "not", "but", "its", "which",
    "wherein", "said", "comprising", "includes", "including", "present",
    "invention", "embodiment", "figure", "claim",
}
CJK = re.compile(r"[\u4e00-\u9fff]")
EN_WORD = re.compile(r"[A-Za-z][A-Za-z0-9-]{2,}")
NUMBER = re.compile(r"\d+(?:\.\d+)?")


def _grams(text: str) -> set[str]:
    chars = CJK.findall(text)
    return {"".join(chars[index : index + 2]) for index in range(len(chars) - 1)}


def _words(text: str) -> list[str]:
    return [word.lower() for word in EN_WORD.findall(text) if word.lower() not in EN_STOP]


def _is_heading(sentence: str) -> bool:
    title = re.sub(r"^#+\s*", "", sentence).strip().lower()
    return title in HEADINGS


def iter_sentences(text: str):
    """Split on sentence marks. A decimal point between digits stays inside the sentence."""
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        parts = re.split(r"(?<=[。！？!?])|(?<=[.!?])(?=\s)", line)
        for part in parts:
            part = part.strip()
            if part:
                yield part


def scan(description: str, disclosure: str) -> dict:
    disclosure_grams = _grams(disclosure)
    disclosure_words = set(_words(disclosure))
    disclosure_numbers = set(NUMBER.findall(disclosure))
    flags = []
    for sentence in iter_sentences(description):
        if len(sentence) < 8 or sentence.startswith("#") or _is_heading(sentence):
            continue
        if sentence in {"【待发明人确认】", "[INVENTOR TO CONFIRM]"}:
            continue
        if sentence in disclosure:
            continue
        reasons = []
        grams = _grams(sentence)
        words = _words(sentence)
        cjk_count = len(CJK.findall(sentence))
        if cjk_count >= 4 and grams:
            recall = len(grams & disclosure_grams) / len(grams)
            if recall < 0.34:
                reasons.append("not_in_locked_disclosure")
        elif len(words) >= 4:
            recall = len(set(words) & disclosure_words) / len(set(words))
            if recall < 0.4:
                reasons.append("not_in_locked_disclosure")
        elif cjk_count < 4 and len(words) < 4:
            continue
        new_numbers = [
            number for number in NUMBER.findall(sentence)
            if number not in disclosure_numbers and number not in {"1", "2", "3", "4", "5", "6", "7", "8", "9"}
        ]
        if new_numbers:
            reasons.append("number_not_in_disclosure")
        if reasons:
            flags.append({"text": sentence, "reasons": reasons, "numbers": new_numbers})
    return {"flags": flags, "flag_count": len(flags), "result": "PASS" if not flags else "FAIL"}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="List description sentences absent from the locked disclosure.")
    parser.add_argument("description", type=Path)
    parser.add_argument("disclosure", type=Path)
    args = parser.parse_args(argv)
    for path in (args.description, args.disclosure):
        if not path.is_file():
            print(f"File not found: {path}", file=sys.stderr)
            return 2
    report = scan(
        args.description.read_text(encoding="utf-8-sig"),
        args.disclosure.read_text(encoding="utf-8-sig"),
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if report["flags"] else 0


if __name__ == "__main__":
    sys.exit(main())
