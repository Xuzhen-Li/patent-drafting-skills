# Formal sheets

Freeze `07-drawings/parts_master.json` before any formal sheet. Draw from
the claims and the disclosure. Do not draw from the abstract alone.

Figure count is as many views as understandability needs. That number may
be zero when the inventor says figures are not required. Do not add a view
to fill a band, and do not drop a view that the claims need.

## Parts master

```json
{
  "frozen": true,
  "parts": [
    {"id": "10", "name": "壳体", "kind": "part"},
    {"id": "S1", "name": "采集", "kind": "step"}
  ],
  "relationships": [
    {"id": "R1", "claim": "1", "text": "壳体容纳传感器", "visible_on": ["图1"]}
  ]
}
```

`frozen` stays false while names are still moving. After the inventor
confirms the names, set `frozen` to true. A new part reopens the master
and invalidates every sheet checksum. `visible_on` may be filled when the
view plan exists; it must name a real sheet before consistency checking.
US and PCT sheet ids are `FIG. 1`, `FIG. 2`.

`numerals.json` is derived from this master. Do not invent a second
numbering.

## Allowed formal sources

| Kind | Source file |
| --- | --- |
| `graphviz` | `.dot`, `.gv` |
| `mermaid` | `.mmd`, `.mermaid` |
| `drawio` | `.drawio` |
| `svg` | `.svg` |
| `matplotlib` | `.py` plotting script |

Export a PNG. The PNG is the sheet. The editable file stays beside it.
`scripts/sheet_checksums.py` writes `sheet_manifest.json` with a sha256 of
the PNG and a sha256 of the source. It refuses to hash until the master
is frozen.

```bash
python3 skills/patent-drawings/scripts/sheet_checksums.py build \
  --drawings <project>/07-drawings \
  --plan <project>/07-drawings/sheet_plan.json \
  --out <project>/07-drawings/sheet_manifest.json
```

`sheet_plan.json` lists `id`, `image`, `source`, and `source_kind` for
each sheet. Exit 1 means nothing was written.

## Rejected sheets

Do not accept any of these as a formal sheet, even as a later "cleanup":

- An image-model bitmap (`source_kind` `image_model`), including a
  picture offered only as a viewpoint.
- Traced art (`traced`, `traced_art`) from a paper, a photograph, or
  another patent.
- An invented spectrum, gel, or curve. `content` of `spectrum`, `gel`, or
  `curve` requires `data_file`, a file the inventor supplied. A smooth
  curve with no data file is rejected.
- An invented chemical structure. `content` `chemical_structure` requires
  `structure_source`, the inventor's structure file or the output of a
  structure editor. A general image model is not that editor.

There is no two-round exception. A rejected picture is not copied into
the fact source and is not hashed into the manifest.

Chemical drawings use a structure tool or the inventor's file. Spectra
and gels use the inventor's data file plus a plotting script. The script
does not generate the measurements.
