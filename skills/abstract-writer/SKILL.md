---
name: abstract-writer
description: >-
  Draft a patent abstract and check its length. CN abstract within 300
  characters, US abstract within 150 words, PCT abstract in English.
  撰写说明书摘要、摘要附图、300字、150 words、摘要不得使用商业性宣传用语、
  其特征在于。
---

# Abstract writer

Write a short abstract of the technical disclosure. CN is Chinese. US and PCT are English. Then run `scripts/check_abstract.py`.

Counting rules and banned wording: [`references/abstract-rules.md`](references/abstract-rules.md). Jurisdiction notes: [`../../shared/jurisdictions.md`](../../shared/jurisdictions.md).

## When to use

- `05-description/description.md` exists and the inventor has confirmed the embodiments.
- The user asks for an abstract (说明书摘要 / abstract) or an abstract figure (摘要附图).

## Inputs

- Locked `04-claims/claims.md` and `05-description/description.md`.
- `07-drawings/` figure list, if figures exist.
- `patent.yaml` field `abstract_figure` when a CN abstract figure is chosen.

## Procedure

1. Read the independent claims and the summary section of the description. The abstract adds no feature, effect, or number that those files do not already contain.
2. CN (专利法第26条第3款; 《专利审查指南》对摘要的字数和用语要求): state the title's subject, the technical problem, the point of the solution, and the principal use. Select one drawing as 摘要附图, the figure that best shows the invention, and set `abstract_figure` in `patent.yaml` to that image file name.
3. US: one paragraph that begins on its own sheet at export. 37 CFR 1.72(b) requires it to be as concise as the disclosure permits, preferably not exceeding 150 words. MPEP 608.01(b) generally uses 50 to 150 words. The checker fails a draft longer than 150 words. The abstract is not used to interpret the claims.
4. PCT: English abstract under PCT Rule 8, preferably 50 to 150 words, and not more than the 150-word check below.
5. Write `06-abstract/abstract.md` as the abstract body only. A leading markdown heading `# 摘要` or `# Abstract` is counted by the script, so leave it out of the file that you check.
6. Run:

```bash
python3 skills/abstract-writer/scripts/check_abstract.py <project>/06-abstract/abstract.md --lang auto
```

Exit 0: within the limit and no warnings. Exit 1: over the limit, even if warnings are also present. Exit 2: within the limit, but claim-like or advertising wording was found; revise and rerun. A missing file path also exits 2.

7. CN character count includes punctuation and excludes whitespace. EN word count is whitespace-separated tokens. The script prints the rule it applied.

## Human gate(s)

No separate named gate. The inventor confirms the abstract text and, for CN, the single 摘要附图, before `consistency-checker`. Record the choice in `LOG.md`.

## Outputs

- `06-abstract/abstract.md`
- `patent.yaml` key `abstract_figure` for CN, matching a file in `07-drawings/`

## Quality checklist

- CN count ≤ 300 characters by the script's rule. EN and PCT ≤ 150 words.
- The problem, the technical point, and the use can be found in the description.
- No `其特征在于`, `其特征是`, or `characterized in that`.
- No puffery (商业性宣传用语): 最佳, 革命性, revolutionary, unique, and the rest of the script's list.
- CN abstract figure is one existing image, not a new drawing invented for the abstract.
- No reference numeral appears unless that numeral is already in `07-drawings/numerals.json`. In a CN abstract, a reference sign is written in parentheses (审查指南).

## Guardrails

- Do not add comparative data, grades, or market claims to make the abstract sound stronger.
- Do not treat the abstract as a claim. Scope stays in `04-claims/claims.md`.
- A warning from the script is a drafting defect to remove, not a style preference to keep.
- The abstract is part of the confidential filing package.

## Next step

If figures are not finished, run `patent-drawings`. When the abstract and the drawings manifest both exist, run `consistency-checker`.
