# Drawing rules checklist (US and PCT)

US utility drawings: 37 CFR 1.84, read with 37 CFR 1.83 (the drawing must show every feature of the invention specified in the claims). PCT drawings: PCT Rule 7 and the physical requirements of PCT Rule 11 (A4). Official text:

- https://www.ecfr.gov/current/title-37/chapter-I/subchapter-A/part-1/section-1.84
- https://www.ecfr.gov/current/title-37/chapter-I/subchapter-A/part-1/section-1.83
- https://www.wipo.int/pct/en/texts/rules/

## Lines and sheets

- [ ] Black ink, durable, uniformly thick and well-defined lines. White background.
- [ ] Each formal sheet comes from an editable source (Graphviz, Mermaid, draw.io, SVG, or a matplotlib script) and has a sha256 in `sheet_manifest.json`. No image-model bitmap, traced art, invented spectrum, or invented structure.
- [ ] No color. Color drawings require a granted petition under 37 CFR 1.84. Do not plan on color.
- [ ] No photograph unless a photograph is the only practical way to show the subject, and the checklist in 37 CFR 1.84 for photographs is met.
- [ ] Views numbered in consecutive Arabic numerals: `FIG. 1`, `FIG. 2`, independent of sheet numbers. Partial views that form one figure use `FIG. 1A`, `FIG. 1B`.
- [ ] The label sits with the view. Do not use `图1` on a US or PCT sheet.
- [ ] US margins follow 37 CFR 1.84 (top 2.5 cm, left 2.5 cm, right 1.5 cm, bottom 1.0 cm). No frame around the sight.
- [ ] PCT sheets are A4 (PCT Rule 11). Keep the same black-line and `FIG.` rules.

## Numbers, letters, and words

- [ ] Reference characters are Arabic numerals where possible, plain and legible, at least 3.2 mm (1/8 inch) high.
- [ ] Lead lines run from the numeral to the part and do not cross each other more than necessary.
- [ ] No descriptive text except a single word or words when absolutely necessary, such as `water`, `steam`, `open`, `closed`, or a section label. Part names stay in the description.
- [ ] No trademark, advertising slogan, or decorative border.

## Consistency with the specification

- [ ] Each numeral has one name. Each name has one numeral.
- [ ] The description uses `housing 10` or `housing (10)`, matching `07-drawings/numerals.json`.
- [ ] Every feature recited in the claims is shown (37 CFR 1.83).
- [ ] The brief description of the drawings lists FIG. 1, FIG. 2, in the same order.
- [ ] Flowcharts use the same step order as the method claim.
- [ ] A numeral is not introduced on a figure and then omitted from the description.

## Manifest

```json
{
  "figures": [
    {"id": "FIG. 1", "numerals": {"10": "housing", "12": "sensor"}}
  ]
}
```

`check_numerals.py` compares this file with the description. Synonyms (`casing` versus `housing`) are reported as two names for one numeral.
