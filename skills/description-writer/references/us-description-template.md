# Description template (US utility and PCT)

Write `05-description/description.md` in English. Do not insert `[0001]` paragraph numbers; `patent-docx-export` adds those to the specification file.

## US section order (37 CFR 1.77(b))

Use this order. Omit a section that does not apply, and say so in `LOG.md` rather than inventing a fact.

1. Title of the invention.
2. Cross-reference to related applications.
3. Statement regarding federally sponsored research or development.
4. The names of the parties to a joint research agreement.
5. Reference to a Sequence Listing, a table, or a computer program listing appendix, if any.
6. Statement regarding prior disclosures by the inventor or a joint inventor.
7. Background of the invention.
8. Brief summary of the invention.
9. Brief description of the drawings.
10. Detailed description of the invention.

37 CFR 1.77(b) continues with (11) a claim or claims and (12) an abstract, each commencing on a separate sheet (37 CFR 1.72(b) for the abstract; 37 CFR 1.75 for the claims). Those two parts are drafted by `claims-drafter` and `abstract-writer` and exported as `claims.docx` and `abstract.docx`. Do not paste them into `description.md`.

The detailed description must still enable and describe the full claim scope (35 U.S.C. §112(a)). Drawings must show the claimed features (37 CFR 1.83).

## PCT (Rule 5)

When `patent.yaml` says `pct`, keep this English file and use these Rule 5 blocks inside the same order: technical field, background art, disclosure of the invention (problem and solution), brief description of the drawings, at least one way of carrying out the invention, and industrial applicability if it is not already obvious from the description. Paper size for PCT is handled at export (A4).

## Skeleton

```
# Title of the Invention

[Title, matching patent.yaml.]

# Cross-Reference to Related Applications

[INVENTOR TO CONFIRM. None known.]

# Statement Regarding Federally Sponsored Research or Development

[INVENTOR TO CONFIRM. No federal sponsorship is recorded in the disclosure.]

# Background of the Invention

[Field sentence.] [Publication number] describes [only what the search note says it describes]. That approach leaves [drawback the inventor stated].

# Brief Summary of the Invention

A sensor device includes a housing and a sensor disposed in the housing. [Repeat each independent claim's features in descriptive sentences. Then the fallbacks.]

[Effects only with inventor-supplied support. Otherwise: [INVENTOR TO CONFIRM].]

# Brief Description of the Drawings

FIG. 1 is a schematic view of a sensor device.
FIG. 2 is a flowchart of a measurement method.

# Detailed Description of the Invention

FIG. 1 shows a sensor device. The sensor device includes a housing 10 and a sensor 12 disposed in the housing 10. [Arrangement the inventor described.]

In another embodiment, [variant from the disclosure]. Values that were not supplied are marked [INVENTOR TO CONFIRM].
```

Write `07-drawings/numerals.json` beside the figures:

```json
{
  "figures": [
    {"id": "FIG. 1", "numerals": {"10": "housing", "12": "sensor"}}
  ]
}
```

Use `housing 10` in the prose so the numeral check can see the pair. One numeral, one name.

## Support matrix

`05-description/support_matrix.md` columns: claim, feature, section heading, `supported` or `confirm`. A row marked `confirm` is an inventor question, not a license to draft the missing fact.
