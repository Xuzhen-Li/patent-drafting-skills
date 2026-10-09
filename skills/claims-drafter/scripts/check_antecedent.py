#!/usr/bin/env python3
"""Check numbered patent claims for dependency defects and antecedent basis.

Language
    --lang zh | en | auto
    auto: Chinese if CJK characters outnumber A–Z letters, otherwise English.
    Dependency patterns for both languages are always applied.

Dependency defects
    (a) a claim cites a number that does not exist, or cites itself or a later claim
    (b) a multiple-dependent claim (two or more parents) is not in the alternative,
        or it depends on another multiple-dependent claim
        CN: 择一引用 uses 或 / 任一项 / 之一; 多项从属权利要求不得作为另一项
        多项从属权利要求的基础
        US / PCT: the same structure is required by 35 U.S.C. §112(e),
        37 CFR 1.75(c), and PCT Rule 6.4

Antecedent basis
    Flag "the/said X" and "所述X" when X was not introduced earlier in that
    claim or in a valid ancestor chain by "a/an X", "至少一/一种/一个/若干 X",
    or a bare mention.

Heuristic limitations
    See LIMITATIONS. This script does not make a legal determination.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

LIMITATIONS = [
    "Noun phrases stop at punctuation, a short function-word list, or a fixed length. This is not a syntactic parse.",
    "Chinese 所述X stops before 的/与/和/及, before another 所述, and before predicate words such as 为, 设置, 密封, 测量, 封闭, 开放. A single trailing location character (内中上下外里侧处) is removed.",
    "A Chinese noun counts as introduced when the same characters occur earlier and are not immediately after 所述. A short noun inside a longer word can therefore count.",
    "English introductions are a/an, at least one, one or more, and a plurality of, plus bare noun sequences. A trailing-word suffix match lets 'the sensor' rest on 'a temperature sensor'.",
    "Plural handling is only a trailing -s, and it is skipped for words ending in -ss.",
    "Dependencies are recognized from 'claim/claims' plus numbers and from 权利要求 patterns (根据/如/引用). Wording such as 'any preceding claim' or 'the first claim' is not resolved.",
    "Each alternative parent of a multiple-dependent claim is checked on its own chain. A term introduced on only one branch is reported.",
    "A line that starts with a number, a period, and a letter or CJK character is a new claim. Decimals such as '1.5 mm' in the middle of a line are not claim numbers.",
]

CLAIM_START = re.compile(
    r"^[ \t]*(\d{1,4})[ \t]*[\.．][ \t]*(?=[A-Za-z\u4e00-\u9fff])",
    re.MULTILINE,
)

EN_CLAIM_REF = re.compile(
    r"\bclaims?\s+(\d+(?:\s*(?:,|，|and|or|to|through|–|—|-)\s*\d+)*)",
    re.IGNORECASE,
)

CN_DEP = re.compile(
    r"(?:根据|如|引用)权利要求\s*"
    r"([0-9０-９]+(?:\s*[-－—–~～至到]\s*[0-9０-９]+|\s*[、，,或和及]\s*[0-9０-９]+)*)"
    r"\s*(?:中)?(?:\s*的)?"
    r"(任一项|任何一项|任一条|之一)?"
)

# Stop at clause punctuation and at 的/与/和/及, which start a new constituent.
# "所述的X" still works because 的 is consumed by the optional 的 before the noun.
_CN_CHAR = r"(?:(?![的与和及])[\u4e00-\u9fff])"
CN_REF = re.compile(rf"所述的?({_CN_CHAR}{{1,16}})")

CN_TAIL_MARKERS = [
    "其特征在于",
    "其特征是",
    "连接于",
    "设置于",
    "设置在",
    "安装在",
    "固定在",
    "用于",
    "位于",
    "包括",
    "具有",
    "设有",
    "通过",
    "连接",
    "设置",
    "固定",
    "安装",
    "封闭",
    "密封",
    "开放",
    "测量",
    "检测",
    "为",
    "是",
    "有",
]

CN_INTRO = re.compile(
    r"(?:至少两个|至少一个|至少一种|至少一|若干|多个|两种|两个|一种|一个|一项|一套|一组)"
    r"([^，、；。\n]{1,40})"
)

TOKEN_RE = re.compile(r"[A-Za-z][A-Za-z0-9-]*|\d+|[()（）\[\],.;:，、；。]")

INTRODUCERS = [
    ["a", "plurality", "of"],
    ["at", "least", "one"],
    ["at", "least", "two"],
    ["one", "or", "more"],
    ["two", "or", "more"],
    ["an"],
    ["a"],
]

STOP_INSIDE_NP = {
    "of", "and", "or", "with", "for", "to", "from", "by", "in", "on", "at",
    "into", "onto", "over", "under", "within", "without", "between", "through",
    "than", "then", "wherein", "comprising", "comprises", "including", "includes",
    "having", "have", "has", "consisting", "consists", "consist", "which", "that",
    "this", "these", "those", "such", "each", "both", "other", "another", "same",
    "following", "further", "thereof", "herein", "hereby", "according", "claim",
    "claims", "is", "are", "was", "were", "be", "being", "been", "as", "when",
    "where", "while", "if", "not", "no", "via", "per", "said", "the",
    "disposed", "configured", "connected", "coupled", "mounted", "arranged",
    "adapted", "operable", "positioned", "located", "formed", "provided",
    "extending", "attached", "fixed", "secured", "placed", "using", "used",
    "containing", "defining",
}

BARE_SKIP = STOP_INSIDE_NP | {
    "a", "an", "at", "least", "one", "more", "two", "plurality", "any",
    "present", "above", "foregoing", "respective",
}

SKIP_EN_PHRASES = {
    "present invention",
    "present disclosure",
    "present application",
    "foregoing",
    "following",
    "same",
    "above",
}

DIGIT_TRANS = str.maketrans("０１２３４５６７８９", "0123456789")


def detect_lang(text: str) -> str:
    cjk = len(re.findall(r"[\u4e00-\u9fff]", text))
    latin = len(re.findall(r"[A-Za-z]", text))
    if cjk == 0 and latin == 0:
        return "en"
    return "zh" if cjk >= latin else "en"


def parse_claims(text: str) -> list[dict]:
    matches = list(CLAIM_START.finditer(text))
    claims = []
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        body = text[match.end() : end].strip()
        claims.append({"number": int(match.group(1)), "text": body})
    return claims


def _dedupe(nums: list[int]) -> list[int]:
    out: list[int] = []
    for num in nums:
        if num not in out:
            out.append(num)
    return out


def expand_en_blob(blob: str) -> list[int]:
    blob = blob.replace("–", "-").replace("—", "-").replace("－", "-")
    nums: list[int] = []
    for match in re.finditer(r"(\d+)\s*(?:(to|through|-)\s*(\d+))?", blob, re.IGNORECASE):
        start = int(match.group(1))
        if match.group(3):
            end = int(match.group(3))
            lo, hi = (start, end) if start <= end else (end, start)
            if hi - lo > 80:
                nums.extend([start, end])
            else:
                nums.extend(range(lo, hi + 1))
        else:
            nums.append(start)
    return _dedupe(nums)


def english_dependencies(text: str) -> tuple[list[int], bool | None]:
    matches = list(EN_CLAIM_REF.finditer(text))
    if not matches:
        return [], None
    nums: list[int] = []
    for match in matches:
        for num in expand_en_blob(match.group(1)):
            if num not in nums:
                nums.append(num)
    if len(nums) <= 1:
        return nums, None
    window = text[max(0, matches[0].start() - 48) : matches[-1].end()]
    alternative = bool(re.search(r"\b(?:or|any)\b", window, re.IGNORECASE))
    return nums, alternative


def expand_cn_blob(blob: str) -> list[int]:
    blob = blob.translate(DIGIT_TRANS)
    blob = (
        blob.replace("－", "-")
        .replace("—", "-")
        .replace("–", "-")
        .replace("～", "-")
        .replace("~", "-")
        .replace("到", "至")
    )
    nums: list[int] = []
    for match in re.finditer(r"(\d+)\s*(?:([-至])\s*(\d+))?", blob):
        start = int(match.group(1))
        if match.group(3):
            end = int(match.group(3))
            lo, hi = (start, end) if start <= end else (end, start)
            if hi - lo > 80:
                nums.extend([start, end])
            else:
                nums.extend(range(lo, hi + 1))
        else:
            nums.append(start)
    return _dedupe(nums)


def chinese_dependencies(text: str) -> tuple[list[int], bool | None]:
    nums: list[int] = []
    alternative_hit = False
    found = False
    for match in CN_DEP.finditer(text):
        found = True
        blob = match.group(1)
        tail = match.group(2) or ""
        if tail or ("或" in blob):
            alternative_hit = True
        for num in expand_cn_blob(blob):
            if num not in nums:
                nums.append(num)
    if not found:
        return [], None
    if len(nums) <= 1:
        return nums, None
    return nums, alternative_hit


def extract_dependencies(text: str) -> tuple[list[int], bool | None]:
    en_nums, en_alt = english_dependencies(text)
    zh_nums, zh_alt = chinese_dependencies(text)
    nums: list[int] = []
    for num in en_nums + zh_nums:
        if num not in nums:
            nums.append(num)
    if len(nums) <= 1:
        return nums, None
    flags = [flag for flag in (en_alt, zh_alt) if flag is not None]
    if not flags:
        return nums, False
    return nums, all(flags)


def _tokenize(text: str) -> list[tuple[str, int, int]]:
    return [(match.group(), match.start(), match.end()) for match in TOKEN_RE.finditer(text)]


def _read_np(tokens: list[tuple[str, int, int]], start: int, max_words: int = 6) -> tuple[list[str], int]:
    words: list[str] = []
    index = start
    while index < len(tokens) and len(words) < max_words:
        tok = tokens[index][0]
        low = tok.lower()
        if not re.match(r"[A-Za-z]", tok):
            break
        if low in STOP_INSIDE_NP:
            break
        words.append(low)
        index += 1
    return words, index


def _match_introducer(tokens: list[tuple[str, int, int]], index: int) -> int:
    lows = [tok[0].lower() for tok in tokens]
    for seq in INTRODUCERS:
        length = len(seq)
        if lows[index : index + length] == seq:
            return length
    return 0


def _add_en_phrase(introduced: set[str], words: list[str]) -> None:
    if not words:
        return
    for length in range(1, len(words) + 1):
        introduced.add(" ".join(words[-length:]))


def collect_en_introduced(text: str) -> set[str]:
    tokens = _tokenize(text)
    introduced: set[str] = set()
    index = 0
    while index < len(tokens):
        low = tokens[index][0].lower()
        if low in ("the", "said"):
            _words, nxt = _read_np(tokens, index + 1)
            index = max(nxt, index + 1)
            continue
        intro_len = _match_introducer(tokens, index)
        if intro_len:
            words, nxt = _read_np(tokens, index + intro_len)
            _add_en_phrase(introduced, words)
            index = max(nxt, index + intro_len)
            continue
        if re.match(r"[A-Za-z]", tokens[index][0]) and low not in BARE_SKIP and len(low) >= 2:
            words, _nxt = _read_np(tokens, index)
            _add_en_phrase(introduced, words)
        index += 1
    return introduced


def _en_variants(phrase: str) -> set[str]:
    variants = {phrase}
    if " " in phrase:
        return variants
    if phrase.endswith("s") and not phrase.endswith("ss") and len(phrase) > 3:
        variants.add(phrase[:-1])
    elif len(phrase) > 2:
        variants.add(phrase + "s")
    return variants


def en_introduced(prior: str, words: list[str]) -> bool:
    if not words:
        return True
    phrase = " ".join(words)
    if phrase in SKIP_EN_PHRASES:
        return True
    introduced = collect_en_introduced(prior)
    return any(variant in introduced for variant in _en_variants(phrase))


def find_en_refs(text: str) -> list[dict]:
    tokens = _tokenize(text)
    refs = []
    index = 0
    while index < len(tokens):
        low = tokens[index][0].lower()
        if low in ("the", "said"):
            words, nxt = _read_np(tokens, index + 1)
            if words and " ".join(words) not in SKIP_EN_PHRASES:
                refs.append(
                    {
                        "kind": "en",
                        "phrase": " ".join(words),
                        "words": words,
                        "start": tokens[index][1],
                    }
                )
            index = max(nxt, index + 1)
            continue
        index += 1
    return refs


def cut_cn_phrase(raw: str) -> str:
    earliest = None
    for marker in CN_TAIL_MARKERS:
        idx = raw.find(marker)
        if idx >= 2 and (earliest is None or idx < earliest):
            earliest = idx
    if earliest is not None:
        raw = raw[:earliest]
    if raw.endswith("之间") and len(raw) > 4:
        raw = raw[:-2]
    elif len(raw) >= 3 and raw[-1] in "内中上下外里侧处":
        raw = raw[:-1]
    return raw


def _add_cn_head(introduced: set[str], head: str) -> None:
    head = "".join(re.findall(r"[\u4e00-\u9fff]", head))[:16]
    if len(head) < 2:
        return
    for length in range(2, len(head) + 1):
        introduced.add(head[-length:])


def collect_cn_introduced(text: str) -> set[str]:
    introduced: set[str] = set()
    for match in CN_INTRO.finditer(text):
        chunk = re.split(r"[与和及]", match.group(1))[0]
        head = chunk.split("的")[-1] if "的" in chunk else chunk
        head = cut_cn_phrase(head)
        _add_cn_head(introduced, head)
    return introduced


def cn_bare(prior: str, phrase: str) -> bool:
    start = 0
    while True:
        idx = prior.find(phrase, start)
        if idx < 0:
            return False
        before = prior[max(0, idx - 3) : idx]
        if before.endswith("所述") or before.endswith("所述的"):
            start = idx + 1
            continue
        return True


def cn_introduced(prior: str, phrase: str) -> bool:
    if len(phrase) < 2:
        return True
    introduced = collect_cn_introduced(prior)
    if phrase in introduced:
        return True
    if any(item.endswith(phrase) and len(phrase) >= 2 for item in introduced):
        return True
    return cn_bare(prior, phrase)


def find_cn_refs(text: str) -> list[dict]:
    refs = []
    for match in CN_REF.finditer(text):
        phrase = cut_cn_phrase(match.group(1))
        if len(phrase) < 2:
            continue
        refs.append({"kind": "zh", "phrase": phrase, "words": [], "start": match.start()})
    return refs


def ancestor_chains(claim: dict, by_num: dict[int, dict], stack: set[int] | None = None) -> list[tuple[str, tuple[int, ...]]]:
    stack = set(stack or ())
    number = claim["number"]
    if number in stack:
        return [("", ())]
    parents = [dep for dep in claim["deps"] if dep in by_num and dep < number]
    if not parents:
        return [("", ())]
    chains: list[tuple[str, tuple[int, ...]]] = []
    for dep in parents:
        parent = by_num[dep]
        for text, chain in ancestor_chains(parent, by_num, stack | {number}):
            merged = (text + "\n" + parent["text"]).strip()
            chains.append((merged, chain + (dep,)))
    return chains or [("", ())]


def _error(code: str, claim: int | None, message: str, **extra) -> dict:
    item = {"code": code, "claim": claim, "message": message}
    item.update(extra)
    return item


def analyze_text(text: str, lang: str = "auto", filename: str | None = None) -> dict:
    chosen = detect_lang(text) if lang == "auto" else lang
    parsed = parse_claims(text)
    errors: list[dict] = []
    if not parsed:
        errors.append(
            _error(
                "no_claims",
                None,
                "No numbered claims were found. Expected lines such as '1. ...' or '1．...'.",
            )
        )
        return _report(filename, chosen, [], errors)

    claims: list[dict] = []
    seen: set[int] = set()
    for claim in parsed:
        if claim["number"] in seen:
            errors.append(
                _error(
                    "duplicate_claim",
                    claim["number"],
                    f"Claim {claim['number']} is numbered more than once. The first copy is kept.",
                )
            )
            continue
        seen.add(claim["number"])
        deps, alt = extract_dependencies(claim["text"])
        claim["deps"] = deps
        claim["alt"] = alt
        claims.append(claim)

    by_num = {claim["number"]: claim for claim in claims}
    for claim in claims:
        missing = sorted({dep for dep in claim["deps"] if dep not in by_num})
        later = sorted({dep for dep in claim["deps"] if dep in by_num and dep >= claim["number"]})
        if missing:
            shown = ", ".join(str(num) for num in missing)
            errors.append(
                _error(
                    "missing_claim",
                    claim["number"],
                    f"Claim {claim['number']} refers to claim {shown}, which does not exist.",
                    refs=missing,
                )
            )
        if later:
            shown = ", ".join(str(num) for num in later)
            errors.append(
                _error(
                    "forward_reference",
                    claim["number"],
                    f"Claim {claim['number']} refers to claim {shown}, which is the same claim or a later claim.",
                    refs=later,
                )
            )
        if len(claim["deps"]) >= 2 and claim["alt"] is False:
            errors.append(
                _error(
                    "multiple_dependent_not_alternative",
                    claim["number"],
                    (
                        f"Claim {claim['number']} refers to more than one claim but not in the alternative. "
                        "Use 或/任一项 in Chinese or 'or'/'any one of' in English "
                        "(专利法实施细则中的择一引用; 35 U.S.C. §112(e); 37 CFR 1.75(c); PCT Rule 6.4)."
                    ),
                    refs=list(claim["deps"]),
                )
            )
        if len(claim["deps"]) >= 2:
            multi_parents = sorted(
                dep
                for dep in claim["deps"]
                if dep in by_num and dep < claim["number"] and len(by_num[dep]["deps"]) >= 2
            )
            if multi_parents:
                shown = ", ".join(str(num) for num in multi_parents)
                errors.append(
                    _error(
                        "multiple_dependent_basis",
                        claim["number"],
                        (
                            f"Claim {claim['number']} is multiple-dependent and depends from "
                            f"multiple-dependent claim {shown}. "
                            "A multiple-dependent claim must not serve as the basis of another "
                            "multiple-dependent claim (多项从属权利要求不得作为另一项多项从属权利要求的基础; "
                            "35 U.S.C. §112(e); 37 CFR 1.75(c); PCT Rule 6.4)."
                        ),
                        parents=multi_parents,
                    )
                )

        chains = ancestor_chains(claim, by_num)
        seen_phrases: set[str] = set()
        for ref in find_cn_refs(claim["text"]) + find_en_refs(claim["text"]):
            if ref["phrase"] in seen_phrases:
                continue
            failing = []
            for chain_text, chain in chains:
                prior = (chain_text + "\n" + claim["text"][: ref["start"]]).strip()
                ok = (
                    cn_introduced(prior, ref["phrase"])
                    if ref["kind"] == "zh"
                    else en_introduced(prior, ref["words"])
                )
                if not ok:
                    failing.append(list(chain))
            if failing:
                seen_phrases.add(ref["phrase"])
                branch_note = ""
                if any(chain for chain in failing):
                    shown = "; ".join(
                        "claim " + "-".join(str(num) for num in chain) if chain else "no valid parent"
                        for chain in failing
                    )
                    branch_note = f" Failing branch: {shown}."
                errors.append(
                    _error(
                        "missing_antecedent",
                        claim["number"],
                        (
                            f"Claim {claim['number']}: \"{ref['phrase']}\" has no earlier introduction "
                            f"in this claim or its ancestor chain.{branch_note}"
                        ),
                        phrase=ref["phrase"],
                        branches=failing,
                    )
                )

    return _report(filename, chosen, claims, errors)


def _claim_public(claim: dict) -> dict:
    return {
        "number": claim["number"],
        "dependencies": list(claim["deps"]),
        "alternative": claim["alt"],
        "multiple_dependent": len(claim["deps"]) >= 2,
    }


def _report(filename: str | None, lang: str, claims: list[dict], errors: list[dict]) -> dict:
    errors = sorted(errors, key=lambda item: ((item["claim"] is None), item["claim"] or 0, item["code"], item.get("phrase", "")))
    return {
        "file": filename,
        "lang": lang,
        "claim_count": len(claims),
        "claims": [_claim_public(claim) for claim in claims],
        "errors": errors,
        "error_count": len(errors),
        "limitations": list(LIMITATIONS),
    }


def analyze_path(path: Path | str, lang: str = "auto") -> dict:
    file_path = Path(path)
    text = file_path.read_text(encoding="utf-8-sig")
    return analyze_text(text, lang=lang, filename=str(file_path))


def render_text(report: dict) -> str:
    lines = [
        "Claim dependency and antecedent report",
        f"File: {report.get('file') or '(text)'}",
        f"Language: {report['lang']}",
        f"Claims parsed: {report['claim_count']}",
        "",
    ]
    if not report["errors"]:
        lines.append("Result: PASS")
    else:
        lines.append(f"ERRORS ({report['error_count']})")
        for error in report["errors"]:
            claim = error["claim"]
            where = f"Claim {claim}" if claim is not None else "File"
            lines.append(f"- [{error['code']}] {where}: {error['message']}")
        lines.append("")
        lines.append("Result: FAIL")
    lines.append("")
    lines.append("Heuristic limitations:")
    for item in report["limitations"]:
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
    parser = argparse.ArgumentParser(
        description="Check claim dependencies and antecedent basis (CN / US / PCT heuristic)."
    )
    parser.add_argument("claims", type=Path, help="Markdown file of numbered claims")
    parser.add_argument("--lang", choices=["zh", "en", "auto"], default="auto")
    parser.add_argument("--format", choices=["text", "json", "both"], default="both")
    args = parser.parse_args(argv)
    if not args.claims.is_file():
        print(f"File not found: {args.claims}", file=sys.stderr)
        return 2
    report = analyze_path(args.claims, lang=args.lang)
    emit(report, args.format)
    return 1 if report["errors"] else 0


if __name__ == "__main__":
    sys.exit(main())
