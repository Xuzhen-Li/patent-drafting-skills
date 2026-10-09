---
name: patent-docx-export
description: >-
  Export the draft to filing-oriented Word files. CN separate 权利要求书,
  说明书, 说明书附图, 说明书摘要, and 摘要附图. US specification, claims,
  and abstract. 导出专利文档、docx、段落编号、[0001]、A4、Letter、宋体、SimSun。
---

# Patent docx export

Build the Word package from the project markdown. Layout details: [`references/docx-layout.md`](references/docx-layout.md). Run this only after `08-consistency/report.md` is `pass`, or after the inventor has accepted each open item in that report.

This produces a drafting package. It does not file the application and it does not fill CNIPA or USPTO forms.

## When to use

- The user asks for the Word filing drafts (权利要求书.docx, specification.docx, or the `09-package/` folder).
- Consistency checking has finished.

## Inputs

- `patent.yaml` — `title`, `jurisdiction`, and for CN `abstract_figure`.
- `04-claims/claims.md`
- `05-description/description.md`
- `06-abstract/abstract.md`
- `07-drawings/` PNG sheets and `07-drawings/sheet_manifest.json`. Markdown notes and editable sources are not sheets.
- A clean `08-consistency/report.md`, including a passing sheet check when drawings exist.

## Procedure

1. Read the consistency report. If status is `blocked`, stop and return to `consistency-checker`.
2. Confirm `description.md` does not already contain `[0001]` numbers. The script adds them.
3. Install dependency if needed: `python3 -m pip install --user python-docx`.
4. Run from the skill repo:

```bash
python3 skills/patent-docx-export/scripts/build_docx.py \
  --jurisdiction cn \
  --project <project> \
  --out <project>/09-package
```

The script flag is lowercase `cn`, `us`, or `pct`. `patent.yaml` stores `CN`, `US`, or `PCT`; pass the lowercase form of that field. `--jurisdiction us` writes the English trio on Letter paper. `--jurisdiction pct` writes the same English file names on A4 (PCT Rule 11).

5. The script recomputes each PNG sha256 and compares it with `sheet_manifest.json`. It embeds those images. It does not redraw them and it does not swap in a different file. Exit 1 if any checksum differs, if a raster file is missing from the manifest, or if a sheet is marked with a forbidden source. Nothing is written in that case. Rebuild the set in `patent-drawings` and rerun consistency before trying again.
6. Open each file and check the items in the layout note: page size, font, paragraph numbers, and that the CN drawing file shows the embedded image rather than a filename list alone.
7. Record the output paths, the consistency-report status, and the sheet hashes in `LOG.md`.

Exit 0: files written. Exit 1: checksum mismatch. Exit 2: missing project files, missing directory, or python-docx is not installed.

## Human gate(s)

Final-package gate (最终文本包). The inventor and a registered patent attorney or patent agent (专利代理师) review the docx set before any filing. Record the gate in `patent.yaml` and `LOG.md` as defined in [`../../shared/gates.md`](../../shared/gates.md). The flag name is `gates.final_package`. The log phrase is `发明人确认文本包` or `I confirm the final package`.

## Outputs

CN, in `--out`:

- `权利要求书.docx`
- `说明书.docx`
- `说明书摘要.docx`
- `说明书附图.docx`
- `摘要附图.docx` — embeds `abstract_figure` when that file passed the checksum
- `sheet_hashes.json` — sha256 of each embedded sheet

US, in `--out`:

- `specification.docx`
- `claims.docx`
- `abstract.docx`
- `drawings.docx` when `07-drawings/` has PNG sheets
- `sheet_hashes.json` when those sheets were embedded

PCT uses the US file names and A4 page size.

## Quality checklist

- CN 说明书 and the US/PCT specification show `[0001]`, `[0002]`, in order. Claims and the abstract do not.
- CN pages are A4. US pages are Letter. PCT pages are A4.
- CN body font is SimSun for Latin runs and 宋体 for East Asian runs. US/PCT body font is Times New Roman.
- Every claim sentence from `claims.md` is present. No claim was shortened for layout.
- The CN drawing file embeds every PNG in the manifest and does not name `figure_list.md` as a figure.
- `abstract_figure` is embedded in `摘要附图.docx`, and its sha256 matches the manifest.
- `sheet_hashes.json` matches the embedded files.
- `【待发明人确认】` and `[INVENTOR TO CONFIRM]` are still visible, not deleted at export.

## Guardrails

- Do not file, pay a fee, or submit to CNIPA, USPTO, or a receiving Office from this skill.
- Do not drop a section to make the document shorter.
- Do not renumber claims during export.
- Do not replace a sheet at export time. A checksum mismatch stops the build.
- If SimSun and 宋体 are not installed on the reading computer, install a Songti-compatible font (Songti SC or Noto Serif CJK SC). The file stores the font names; it does not embed the font.
- The package remains confidential. Public disclosure before filing can destroy novelty (专利法第24条; 35 U.S.C. §102(b)(1)).

## Next step

Stop. The next actor is the inventor and the patent agent or attorney, using the final-package gate. Further draft edits return to the skill that owns that section, then to `consistency-checker`, then here again.
