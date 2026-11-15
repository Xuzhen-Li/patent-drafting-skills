---
name: consistency-checker
description: >-
  Cross-check claims, description, drawings, and abstract before export.
  Antecedent basis, dependency rules, abstract length, reference numerals,
  claim support, and consistent terms.
---

# Consistency checker

Compare the locked claim set, the description, the drawings manifest, and the abstract, then write `08-consistency/report.md`. Do not alter technical content merely to silence a check; either fix the draft or flag the item for the inventor.

Scripts:

- `../claims-drafter/scripts/check_antecedent.py`
- `../abstract-writer/scripts/check_abstract.py`
- `scripts/check_numerals.py`
- `scripts/check_sheets.py`

Gate list: [`../../shared/gates.md`](../../shared/gates.md). Chinese-to-English terms, when the inventor's notes are in Chinese: [`../../shared/glossary_cn_en.md`](../../shared/glossary_cn_en.md).

## When to use

- Claims, description, and the abstract exist. When `patent.yaml` `drawings` is not `none`, `07-drawings/numerals.json` (created by `description-writer` and updated by `patent-drawings`) and `07-drawings/figure_list.md` (from `patent-drawings`) also exist. `drawings: none` means the inventor recorded that no figure is required, so there is no figure list to check.
- The user requests a consistency check or a pre-export review.

## Inputs

- `04-claims/claims.md`, `04-claims/claim_map.md`
- `05-description/description.md`, `05-description/support_matrix.md`
- `06-abstract/abstract.md`
- `07-drawings/numerals.json`, `figure_list.md`, `parts_master.json`, `sheet_manifest.json`, and the PNG sheets, unless `drawings` is `none`
- Report skeleton: [`references/report-template.md`](references/report-template.md)

## Procedure

1. Copy the report template to `08-consistency/report.md`. Record the jurisdiction and the date of the files rather than a guessed filing date.
2. Antecedent and dependencies:

```bash
python3 skills/claims-drafter/scripts/check_antecedent.py <project>/04-claims/claims.md --lang en --format both
```

Paste the error list into the report. Exit code 0 is required before export. Inspect the JSON `limitations` and note any phrase the heuristic cannot see (`any preceding claim`, `the first claim`, plurals other than a trailing -s).

3. Abstract:

```bash
python3 skills/abstract-writer/scripts/check_abstract.py <project>/06-abstract/abstract.md --lang en --format both
```

Exit code 0 is required. Exit code 2 means the wording must be rewritten; exit code 1 means the abstract must be shortened.

4. Numerals. If `drawings` is `none`, skip the script and record in the report that the inventor noted no figures. Otherwise, run:

```bash
python3 skills/consistency-checker/scripts/check_numerals.py \
  <project>/05-description/description.md \
  <project>/07-drawings/numerals.json \
  --format both
```

The manifest format is `{"figures":[{"id":"FIG. 1","numerals":{"10":"housing"}}]}`. The script exits with code 1 until every error code below is resolved or explicitly accepted by the inventor:

- `numeral_missing_in_text` — present on a figure, absent from the description
- `numeral_missing_in_drawings` — present in the description, absent from the manifest
- `numeral_multiple_names` — one numeral assigned two names
- `name_multiple_numerals` — one name assigned two numerals

5. Sheets, unless `drawings` is `none`. Open every PNG file; do not pass any sheet you have not opened. Record the look in `07-drawings/visual_look.json`: for each sheet id, `numerals_match_master` and `relationships_seen`. Then run:

```bash
python3 skills/consistency-checker/scripts/check_sheets.py \
  --drawings <project>/07-drawings \
  --look <project>/07-drawings/visual_look.json \
  --format both
```

The script decodes each PNG, verifies its sha256 checksum, and checks for black lines on a white background. Any colored pixel or shading fails even if the look file says otherwise. Each relationship in `parts_master.json` must identify the figure where it is visible (`visible_on`). The script exits with code 1 until all error codes are resolved. Any checksum mismatch, unreadable image, or black-on-white failure invalidates the entire set: return to `patent-drawings`, rebuild every sheet, and inspect them again rather than passing the remaining sheets.

- `checksum_mismatch` — the PNG changed after the manifest was written
- `not_black_on_white` / `blank_sheet` — the decoded pixels fail the black-on-white check
- `visual_look_missing` / `numeral_look_failed` — the numerals on that image were not confirmed
- `relationship_without_figure` / `relationship_not_seen` — a claimed relationship lacks a figure, or the look did not record it there
- `image_unreadable` — the file could not be opened as a PNG

6. Support matrix. For each claim feature, the description row is marked `supported` only when the same noun and the same relationship appear in the brief summary or the detailed description (35 U.S.C. §112(a); PCT Article 6). A `confirm` row blocks export. Where the claims promise a figure, name that figure. "Somewhere in the drawings" is not enough.
7. Terminology pass. Use one noun per concept consistently across the claims, description, abstract, and `numerals.json`. Do not mix a translated term with the original term.
8. Abstract new-matter pass. Confirm that every noun in the abstract already appears in the description and that the abstract introduces no new results.
9. Set the report status to `pass` or `blocked`. A `blocked` report lists the owner of each open item; drawing failures belong to `patent-drawings`.

## Human gate(s)

The final-package gate requires this report to be in `pass` status, or requires a written inventor decision for each remaining open item. Export cannot begin while the status is `blocked`.

## Outputs

- `08-consistency/report.md`
- Optional JSON copies alongside it if the user wants the raw script output (`claims.json`, `abstract.json`, `numerals.json`)

## Quality checklist

- All three scripts were run against the current files, and the report quotes their exit codes.
- No forward claim references, missing claims, non-alternative multiple dependencies, or multiple-dependent claims depending on another multiple-dependent claim.
- Antecedent defects flagged by the script are either fixed or listed along with the failing branch.
- Numeral names match exactly after the script's cleanup (`housing` and `Housing` match; `housing` and `casing` do not).
- The support matrix contains no empty feature cells.
- The abstract length check exits with code 0.
- When drawings exist, `check_sheets.py` was run, every sheet row records `opened=true`, and no relationship lacks a figure.

## Guardrails

- Do not delete a claim feature or a numeral just to make a script exit with code 0. Ask which text is wrong: the claim, the description, or the figure.
- Do not waive a pixel failure from the look file. Return the set to `patent-drawings`.
- Do not treat a passing script run as legal clearance; the documented limitations of each script still apply.
- Do not invent a prior-art citation while "fixing" the background section.
- Keep the package confidential.

## Next step

Proceed to `patent-docx-export` once the report status is `pass`.
