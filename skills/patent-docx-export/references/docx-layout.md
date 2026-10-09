# Docx layout

`build_docx.py` converts the project markdown into separate Word files. It is a drafting layout, not a bureau-specific XML filing.

## Command

```bash
python3 skills/patent-docx-export/scripts/build_docx.py \
  --jurisdiction cn|us|pct \
  --project <project-dir> \
  --out <project-dir>/09-package
```

Requires `python-docx`. If it is missing, the process exits 2 and prints an install hint.

Required files:

- `04-claims/claims.md`
- `05-description/description.md`
- `06-abstract/abstract.md`

Optional:

- `patent.yaml` keys `title` and `abstract_figure` (flat `key: value` lines).
- `07-drawings/*.png` plus `07-drawings/sheet_manifest.json` when any raster sheet exists. Editable sources (`.dot`, `.mmd`, `.drawio`, `.svg`, `.py`) are not embedded.

## Jurisdiction

`patent.yaml` stores `CN`, `US`, or `PCT`. This script's `--jurisdiction` flag is the same choice in lowercase: `cn`, `us`, or `pct`.

| Mode | Paper | Font | Files | Paragraph numbers |
| --- | --- | --- | --- | --- |
| `cn` | A4 (210 mm × 297 mm) | Latin runs SimSun; East Asian runs 宋体; size 12 pt | 权利要求书.docx, 说明书.docx, 说明书摘要.docx, 说明书附图.docx, 摘要附图.docx | 说明书 only, `[0001]` |
| `us` | Letter (8.5 in × 11 in), 1.5 line spacing | Times New Roman, 12 pt | specification.docx, claims.docx, abstract.docx | specification only, `[0001]` |
| `pct` | A4, 1.5 line spacing | Times New Roman, 12 pt | same names as `us` | specification only, `[0001]` |

US claims and the abstract are separate files so each can start on its own sheet (37 CFR 1.72(b), 37 CFR 1.75). CN practice files 权利要求书, 说明书, 说明书附图, 说明书摘要, and 摘要附图 as separate documents. `说明书附图.docx` embeds each PNG in manifest order, with the figure id and the sha256. `摘要附图.docx` embeds `abstract_figure` only. US and PCT write `drawings.docx` the same way when PNGs exist. `sheet_hashes.json` sits next to the Word files.

## Markdown handling

- A blank line starts a new paragraph.
- A line `# Heading` becomes a paragraph of the heading text, without the hash marks.
- A line that begins with `1.` or `1．` starts a new paragraph, so each claim stays intact.
- The description should not already contain `[0001]`. The exporter prefixes those numbers itself.
- `patent.yaml` `title` is an unnumbered first line. It does not consume `[0001]`.

## Font fallback

The CN file names SimSun (ASCII / hAnsi) and 宋体 (east Asia). Word or WPS substitutes a Songti face when those fonts are absent. On macOS the usual install is Songti SC or Noto Serif CJK SC. The exporter does not embed font files.

## Drawings

Before any Word file is saved, each raster file in `07-drawings/` is hashed and compared with `sheet_manifest.json`. A mismatch, a missing manifest, an extra PNG, or a forbidden `source_kind` (`image_model`, `traced`, `traced_art`, `invented_spectrum`, `invented_structure`) stops the export. The script does not redraw.

`说明书附图.docx` and, for US/PCT, `drawings.docx` embed the PNGs. `摘要附图.docx` embeds only `abstract_figure`. A chosen file that is not in the verified set is marked `【待发明人确认】` and is not replaced with another image.

## Exit codes

| Code | Meaning |
| --- | --- |
| 0 | Files written |
| 1 | A sheet checksum does not match, or a sheet is not the file that passed review |
| 2 | Bad arguments, project directory missing, a required markdown file missing, or python-docx not installed |
