---
name: abstract-writer
description: >-
  Draft an English patent abstract and check its length: US abstract
  within 150 words, PCT abstract in English. No claim wording, no
  advertising words.
---

# Abstract writer

Write a short abstract of the technical disclosure in English. Then run `scripts/check_abstract.py`.

Counting rules and banned wording: [`references/abstract-rules.md`](references/abstract-rules.md). Jurisdiction notes: [`../../shared/jurisdictions.md`](../../shared/jurisdictions.md).

## When to use

- `05-description/description.md` exists and the inventor has confirmed the embodiments.
- The user asks for an abstract.

## Inputs

- Locked `04-claims/claims.md` and `05-description/description.md`.
- `07-drawings/` figure list, if figures exist.

## Procedure

1. Read the independent claims and the summary section of the description. The abstract adds no feature, effect, or number that those files do not already contain.
2. US: one paragraph that begins on its own sheet at export. 37 CFR 1.72(b) requires it to be as concise as the disclosure permits, preferably not exceeding 150 words. MPEP 608.01(b) generally uses 50 to 150 words. The checker fails a draft longer than 150 words. The abstract is not used to interpret the claims.
3. PCT: English abstract under PCT Rule 8, preferably 50 to 150 words, and not more than the 150-word check below.
4. Write `06-abstract/abstract.md` as the abstract body only. A leading markdown heading `# Abstract` is counted by the script, so leave it out of the file that you check.
5. Run:

```bash
python3 skills/abstract-writer/scripts/check_abstract.py <project>/06-abstract/abstract.md --lang en
```

Exit 0: within the limit and no warnings. Exit 1: over the limit, even if warnings are also present. Exit 2: within the limit, but claim-like or advertising wording was found; revise and rerun. A missing file path also exits 2.

6. Word count is whitespace-separated tokens. The script prints the rule it applied.

## Human gate(s)

No separate named gate. The inventor confirms the abstract text before `consistency-checker`. Record the choice in `LOG.md`.

## Outputs

- `06-abstract/abstract.md`

## Quality checklist

- US and PCT ≤ 150 words.
- The problem, the technical point, and the use can be found in the description.
- No `characterized in that`.
- No puffery: revolutionary, unique, and the rest of the script's list.
- No reference numeral appears unless that numeral is already in `07-drawings/numerals.json`.

## Guardrails

- Do not add comparative data, grades, or market claims to make the abstract sound stronger.
- Do not treat the abstract as a claim. Scope stays in `04-claims/claims.md`.
- A warning from the script is a drafting defect to remove, not a style preference to keep.
- The abstract is part of the confidential filing package.

## Next step

If figures are not finished, run `patent-drawings`. When the abstract and the drawings manifest both exist, run `consistency-checker`.
