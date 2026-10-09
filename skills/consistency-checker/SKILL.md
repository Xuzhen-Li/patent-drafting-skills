---
name: consistency-checker
description: >-
  Cross-check claims, description, drawings, and abstract before export.
  Antecedent basis, dependency rules, abstract length, and reference numerals.
  一致性检查、附图标记核对、权利要求支持、术语一致、所述、antecedent、
  多项从属、摘要字数。
---

# Consistency checker

Compare the locked claim set, the description, the drawings manifest, and the abstract. Write `08-consistency/report.md`. Do not change technical content in order to silence a check. Either fix the draft or mark the item for the inventor.

Scripts:

- `../claims-drafter/scripts/check_antecedent.py`
- `../abstract-writer/scripts/check_abstract.py`
- `scripts/check_numerals.py`

Gate list: [`../../shared/gates.md`](../../shared/gates.md). Term pairs: [`../../shared/glossary_cn_en.md`](../../shared/glossary_cn_en.md).

## When to use

- Claims, description, and the abstract exist. When `patent.yaml` `drawings` is not `none`, `07-drawings/numerals.json` (from `description-writer`, then updated by `patent-drawings`) and `07-drawings/figure_list.md` (from `patent-drawings`) exist too. `drawings: none` means the inventor recorded that no figure is required, so there is no figure list to check.
- The user asks for a consistency check (一致性检查) or a pre-export review.

## Inputs

- `04-claims/claims.md`, `04-claims/claim_map.md`
- `05-description/description.md`, `05-description/support_matrix.md`
- `06-abstract/abstract.md`
- `07-drawings/numerals.json` and `07-drawings/figure_list.md`, unless `drawings` is `none`
- Report skeleton: [`references/report-template.md`](references/report-template.md)

## Procedure

1. Copy the report template to `08-consistency/report.md`. Record jurisdiction and the date of the files, not a guessed filing date.
2. Antecedent and dependencies:

```bash
python3 skills/claims-drafter/scripts/check_antecedent.py <project>/04-claims/claims.md --lang auto --format both
```

Paste the error list into the report. Exit 0 is required before export. Read the JSON `limitations` and note any phrase the heuristic cannot see (`any preceding claim`, a noun split by 的).

3. Abstract:

```bash
python3 skills/abstract-writer/scripts/check_abstract.py <project>/06-abstract/abstract.md --lang auto --format both
```

Exit 0 is required. Exit 2 means wording must be rewritten. Exit 1 means the abstract must be shortened.

4. Numerals. If `drawings` is `none`, skip the script and write in the report that the inventor recorded no figures. Otherwise run:

```bash
python3 skills/consistency-checker/scripts/check_numerals.py \
  <project>/05-description/description.md \
  <project>/07-drawings/numerals.json \
  --format both
```

The manifest shape is `{"figures":[{"id":"FIG. 1","numerals":{"10":"housing"}}]}`. CN ids look like `图1`, and names are Chinese. Exit 1 until every code below is cleared or explicitly accepted by the inventor:

- `numeral_missing_in_text` — on a figure, absent from the description
- `numeral_missing_in_drawings` — in the description, absent from the manifest
- `numeral_multiple_names` — one numeral, two names
- `name_multiple_numerals` — one name, two numerals

5. Support matrix. For each claim feature, the description row is `supported` only when the same noun and the same relationship appear in 发明内容 or 具体实施方式 (or the US brief summary and detailed description). 专利法第26条第4款; 35 U.S.C. §112(a). A `confirm` row blocks export.
6. Term pass. One concept, one noun, in the claim, the description, the abstract, and `numerals.json`. Use the glossary for CN/EN pairs. Do not translate inside a single-language filing.
7. Abstract new-matter pass. Every noun in the abstract already occurs in the description. The abstract does not add a result.
8. Set the report status to `pass` or `blocked`. `blocked` lists the owner of each open item (inventor or drafter).

## Human gate(s)

The final-package gate (最终文本包) requires this report in `pass` status, or a written inventor decision on each remaining item. Export does not start on `blocked`.

## Outputs

- `08-consistency/report.md`
- Optional JSON copies next to it if the user wants the raw script output (`claims.json`, `abstract.json`, `numerals.json`)

## Quality checklist

- All three scripts were run on the current files, and the report quotes their exit codes.
- No forward claim reference, no missing claim, no non-alternative multiple dependency, no multiple-dependent claim depending on another multiple-dependent claim.
- Antecedent defects from the script are fixed or listed with the branch that failed.
- Numeral names match exactly after the script's cleanup (`housing` and `Housing` match; `壳体` and `盖体` do not).
- The support matrix has no empty feature cells.
- The abstract length check is exit 0.

## Guardrails

- Do not delete a claim feature or a numeral only to make a script exit 0. Ask which text is wrong: the claim, the description, or the figure.
- Do not treat a script pass as a legal clearance. The limitations in each script still apply.
- Do not invent a prior-art citation while "fixing" the background section.
- Leave the package confidential.

## Next step

`patent-docx-export` when the report status is `pass`.
