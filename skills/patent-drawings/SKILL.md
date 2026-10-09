---
name: patent-drawings
description: >-
  Plan and produce black-and-white patent drawings with consistent reference
  numerals. CN 图1 rules and US FIG. 1 rules, plus a numerals manifest.
  专利附图、说明书附图、摘要附图、附图标记、黑白线条图、图1、FIG. 1、
  流程图、框图、结构示意图。
---

# Patent drawings

Plan the figure set, draw it with a line-drawing tool, and record every reference numeral. CN figure labels are 图1, 图2. US and PCT labels are FIG. 1, FIG. 2.

Checklists: [`references/drawing-rules-cn.md`](references/drawing-rules-cn.md), [`references/drawing-rules-us.md`](references/drawing-rules-us.md). Terms: [`../../shared/glossary_cn_en.md`](../../shared/glossary_cn_en.md).

## When to use

- The description names parts or steps that a figure must show.
- The user asks for patent drawings (专利附图), a flowchart, a block diagram, or a schematic.

## Inputs

- `00-disclosure/disclosure.md` and `04-claims/claims.md`. Do not draw from the abstract alone.
- `05-description/description.md`, especially 附图说明 / brief description of the drawings.
- Claimed structure must be visible (37 CFR 1.83 for US; CN practice expects the drawings to match the description).
- Source rules: [`references/sheet-sources.md`](references/sheet-sources.md).

## Procedure

1. Freeze `07-drawings/parts_master.json` before any sheet. List every part and step the disclosure actually names. Set `frozen` to true only after the inventor confirms the names. Later views are derived from this master. A conflicting fact waits. Do not add a part to make a view look complete.
2. List figures in `07-drawings/figure_list.md`. One row: figure id, type, what it shows, source embodiment. Types: structure (结构示意图), flowchart (流程图), block diagram (框图), schematic (原理图), cross-section (剖视图). Use as many views as understandability needs, including none when the inventor says so. Do not add a filler view.
3. Derive `07-drawings/numerals.json` from the master. One part keeps one number in every figure. One number keeps one name.
4. Save the numeral manifest:

```json
{
  "figures": [
    {"id": "图1", "numerals": {"10": "壳体", "12": "传感器"}}
  ]
}
```

US/PCT ids are `FIG. 1`, `FIG. 2`. Names must be the nouns used in the description (`housing`, not a synonym).

5. Draw black lines on a white ground. No color, shading, photographs, or grayscale fills, unless the inventor has a specific reason that the CN or US checklist allows.
6. Put no text in the figure except a word that is necessary (for example a flow-node verb, `open`/`closed`, or a section mark). Part names live in the description, not as captions inside the figure.
7. Label the figure 图1 or FIG. 1 under the view, in order.
8. Produce each formal sheet from an editable source, then export PNG. Allowed sources are Graphviz (`.dot`), Mermaid (`.mmd`), draw.io (`.drawio`), SVG (`.svg`), and a matplotlib script (`.py`). Reject image-model bitmaps, traced art, invented structures, and invented spectra. A curve or a gel needs the inventor's data file. A chemical structure needs the inventor's structure file. Details and the checksum command are in [`references/sheet-sources.md`](references/sheet-sources.md).
9. Run `scripts/sheet_checksums.py build` so `sheet_manifest.json` stores a sha256 for each PNG and its source. If any sheet is rejected, fix the source and rebuild the whole set. Do not keep a passing subset.
10. CN: pick the single 摘要附图 from this set and set `patent.yaml` `abstract_figure` to that file name. Do not draw a new abstract-only figure.
11. Walk the jurisdiction checklist and fix every open item before consistency checking.

## Human gate(s)

The inventor confirms `parts_master.json`, `figure_list.md`, and the numeral names before the figures are treated as final. This confirmation is recorded in `LOG.md`. It is not a substitute for the final-package gate.

## Outputs

- `07-drawings/parts_master.json` — frozen parts and steps
- `07-drawings/figure_list.md`
- `07-drawings/numerals.json` — derived from the master
- `07-drawings/sheet_plan.json` and `07-drawings/sheet_manifest.json` — sha256 per sheet
- PNG sheets and their editable sources (`.dot`, `.mmd`, `.drawio`, `.svg`, or `.py`)
- Updated 附图说明 / brief description of the drawings if a figure was added

## Quality checklist

- Black lines, white background, readable at reproduction size.
- CN labels are 图1. US and PCT labels are FIG. 1. Numbering has no gaps.
- Every numeral in the manifest appears in the description as `name 10` or `名称10` / `名称(10)`.
- The same part is not given two numbers. The same number is not given two names.
- Claimed structure is on a figure. Flowcharts use the same step order as the method claim.
- The sheet contains no advertising, color key, or photograph of a commercial product.
- Every formal PNG has an allowed editable source and a matching sha256 in `sheet_manifest.json`.
- No image-model bitmap, traced figure, invented spectrum, or invented structure was hashed.
- PCT sheets are A4. US sheets follow 37 CFR 1.84. CN sheets follow the CN checklist.

## Guardrails

- Do not add a part to a figure that the disclosure does not describe. A missing part is `【待发明人确认】` / `[INVENTOR TO CONFIRM]` in `figure_list.md`, not a guessed component.
- Do not trace a figure from another patent or from a photograph. Draw from the inventor's disclosure.
- Do not send an image-model picture, a traced picture, or a curve without the inventor's data file through the checksum script. There is no second-round exception.
- Reference numerals are not a second claim. They identify parts.
- Keep the drawing files inside the project. They are confidential before filing.

## Next step

`consistency-checker`, after `06-abstract/abstract.md` exists. The numeral script reads `05-description/description.md` and `07-drawings/numerals.json`. The sheet script opens each PNG named in `sheet_manifest.json`. A failure here is fixed in this skill, then the whole set is hashed again.
