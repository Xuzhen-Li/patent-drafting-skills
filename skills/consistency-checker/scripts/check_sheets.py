#!/usr/bin/env python3
"""Open each formal sheet, check pixels, checksums, and named relationships.

The script decodes each PNG in sheet_manifest.json. It records width, height,
and whether the pixels are black lines on white. A chromatic pixel, or a
mid-gray shading fraction above 5 percent, fails the sheet. A blank white
sheet fails because no line was drawn.

visual_look.json is the record that someone looked at the open image and
checked numerals against the parts master. Pixel failures cannot be waived
by that file. A claimed relationship with no figure, or a figure that was
not looked at, fails. Any failure fails the whole set.

    check_sheets.py --drawings <07-drawings> [--look visual_look.json] --format both

Exit codes
    0  no defects
    1  one or more defects
    2  missing manifest or invalid JSON
"""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
import sys
import zlib
from pathlib import Path

DARK_MAX = 40
WHITE_MIN = 220
CHROMA_GAP = 16
MID_FRACTION = 0.05


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 16), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _paeth(left: int, up: int, upper_left: int) -> int:
    estimate = left + up - upper_left
    if abs(estimate - left) <= abs(estimate - up) and abs(estimate - left) <= abs(estimate - upper_left):
        return left
    if abs(estimate - up) <= abs(estimate - upper_left):
        return up
    return upper_left


def _unfilter(filter_type: int, row: bytearray, prev: bytearray, channels: int) -> None:
    if filter_type == 0:
        return
    if filter_type == 1:
        for index in range(len(row)):
            left = row[index - channels] if index >= channels else 0
            row[index] = (row[index] + left) & 255
        return
    if filter_type == 2:
        for index in range(len(row)):
            row[index] = (row[index] + prev[index]) & 255
        return
    if filter_type == 3:
        for index in range(len(row)):
            left = row[index - channels] if index >= channels else 0
            row[index] = (row[index] + ((left + prev[index]) // 2)) & 255
        return
    if filter_type == 4:
        for index in range(len(row)):
            left = row[index - channels] if index >= channels else 0
            up = prev[index]
            upper_left = prev[index - channels] if index >= channels else 0
            row[index] = (row[index] + _paeth(left, up, upper_left)) & 255
        return
    raise ValueError(f"unsupported PNG filter {filter_type}")


def read_png(data: bytes) -> tuple[int, int, list[tuple[int, int, int]]]:
    signature = b"\x89PNG\r\n\x1a\n"
    if not data.startswith(signature):
        raise ValueError("not a PNG")
    pos = 8
    width = height = color_type = None
    idat = bytearray()
    while pos + 8 <= len(data):
        length = struct.unpack(">I", data[pos : pos + 4])[0]
        tag = data[pos + 4 : pos + 8]
        start = pos + 8
        chunk = data[start : start + length]
        pos = start + length + 4
        if tag == b"IHDR":
            width, height, bit_depth, color_type, compression, filter_method, interlace = struct.unpack(
                ">IIBBBBB", chunk
            )
            if bit_depth != 8 or compression != 0 or filter_method != 0 or interlace != 0:
                raise ValueError("unsupported PNG header")
            if color_type not in (0, 2, 4, 6):
                raise ValueError("unsupported PNG color type")
        elif tag == b"IDAT":
            idat.extend(chunk)
        elif tag == b"IEND":
            break
    if width is None or height is None or color_type is None or not idat:
        raise ValueError("incomplete PNG")
    channels = {0: 1, 2: 3, 4: 2, 6: 4}[color_type]
    raw = zlib.decompress(bytes(idat))
    stride = width * channels
    expected = height * (stride + 1)
    if len(raw) < expected:
        raise ValueError("PNG pixel data is short")
    pixels: list[tuple[int, int, int]] = []
    prev = bytearray(stride)
    cursor = 0
    for _ in range(height):
        filter_type = raw[cursor]
        cursor += 1
        row = bytearray(raw[cursor : cursor + stride])
        cursor += stride
        _unfilter(filter_type, row, prev, channels)
        prev = row
        if channels == 1:
            pixels.extend((value, value, value) for value in row)
        elif channels == 2:
            pixels.extend((row[index], row[index], row[index]) for index in range(0, stride, 2))
        elif channels == 3:
            pixels.extend((row[index], row[index + 1], row[index + 2]) for index in range(0, stride, 3))
        else:
            pixels.extend((row[index], row[index + 1], row[index + 2]) for index in range(0, stride, 4))
    return width, height, pixels


def black_on_white(pixels: list[tuple[int, int, int]]) -> dict:
    colored = 0
    dark = 0
    mid = 0
    white = 0
    for red, green, blue in pixels:
        if max(red, green, blue) - min(red, green, blue) > CHROMA_GAP:
            colored += 1
        luminance = (red + green + blue) / 3
        if luminance <= DARK_MAX:
            dark += 1
        elif luminance >= WHITE_MIN:
            white += 1
        else:
            mid += 1
    total = len(pixels) or 1
    ok = colored == 0 and dark >= 1 and (mid / total) <= MID_FRACTION
    return {
        "black_on_white": ok,
        "colored_pixels": colored,
        "dark_pixels": dark,
        "mid_pixels": mid,
        "white_pixels": white,
    }


def _load(path: Path) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON in {path.name}: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError(f"{path.name} must be a JSON object")
    return data


def _defect(code: str, sheet: str, message: str) -> dict:
    return {"code": code, "sheet": sheet, "message": message}


def analyze(drawings: Path, look: dict | None) -> dict:
    defects: list[dict] = []
    master_path = drawings / "parts_master.json"
    manifest_path = drawings / "sheet_manifest.json"
    if not master_path.is_file():
        raise ValueError("parts_master.json is missing")
    if not manifest_path.is_file():
        raise ValueError("sheet_manifest.json is missing")
    master = _load(master_path)
    manifest = _load(manifest_path)
    if master.get("frozen") is not True:
        defects.append(_defect("master_not_frozen", "", "The parts master is not frozen."))

    sheets = manifest.get("sheets")
    if not isinstance(sheets, list) or not sheets:
        defects.append(_defect("manifest_empty", "", "No sheets are listed."))
        sheets = []

    look_by_id: dict[str, dict] = {}
    if look is None:
        defects.append(_defect("visual_look_missing", "", "No visual look record. Open each image and record the look."))
    else:
        entries = look.get("sheets")
        if not isinstance(entries, list):
            defects.append(_defect("visual_look_missing", "", "visual_look.json has no sheets list."))
        else:
            for entry in entries:
                if isinstance(entry, dict) and entry.get("id"):
                    look_by_id[str(entry["id"])] = entry

    relationships = master.get("relationships") or []
    if not isinstance(relationships, list):
        relationships = []
    sheet_ids = {str(sheet.get("id")) for sheet in sheets if isinstance(sheet, dict)}
    rel_ids_by_sheet: dict[str, list[str]] = {sheet_id: [] for sheet_id in sheet_ids}
    for rel in relationships:
        if not isinstance(rel, dict):
            defects.append(_defect("relationship_without_figure", "", "A relationship is not an object."))
            continue
        rel_id = str(rel.get("id") or "")
        visible = rel.get("visible_on") or []
        if isinstance(visible, str):
            visible = [visible]
        if not rel_id or not isinstance(visible, list) or not visible:
            defects.append(
                _defect(
                    "relationship_without_figure",
                    "",
                    f"Relationship '{rel_id or '?'}' does not name a figure.",
                )
            )
            continue
        unknown = [item for item in visible if str(item) not in sheet_ids]
        if unknown:
            defects.append(
                _defect(
                    "relationship_without_figure",
                    ",".join(str(item) for item in unknown),
                    f"Relationship '{rel_id}' names a figure that is not in the manifest.",
                )
            )
        for item in visible:
            if str(item) in rel_ids_by_sheet:
                rel_ids_by_sheet[str(item)].append(rel_id)

    opened = []
    for sheet in sheets:
        if not isinstance(sheet, dict):
            defects.append(_defect("manifest_sheet_invalid", "", "A manifest sheet is not an object."))
            continue
        sheet_id = str(sheet.get("id") or "")
        image_name = str(sheet.get("image") or "")
        image_path = drawings / image_name
        row = {"id": sheet_id, "image": image_name, "opened": False}
        if not image_path.is_file():
            defects.append(_defect("missing_image", sheet_id, f"Missing {image_name}."))
            opened.append(row)
            continue
        actual = sha256_file(image_path)
        expected = str(sheet.get("sha256") or "").lower()
        row["sha256_ok"] = actual == expected
        if actual != expected:
            defects.append(
                _defect(
                    "checksum_mismatch",
                    sheet_id,
                    f"{image_name} checksum changed. Restart the whole set.",
                )
            )
        try:
            width, height, pixels = read_png(image_path.read_bytes())
        except (ValueError, zlib.error) as exc:
            defects.append(_defect("image_unreadable", sheet_id, str(exc)))
            opened.append(row)
            continue
        stats = black_on_white(pixels)
        row.update({"opened": True, "width": width, "height": height, **stats})
        if not stats["black_on_white"]:
            if stats["dark_pixels"] == 0 and stats["mid_pixels"] == 0 and stats["colored_pixels"] == 0:
                reason = "blank_sheet"
            else:
                reason = "not_black_on_white"
            defects.append(_defect(reason, sheet_id, f"{image_name} is not black lines on white."))
        opened.append(row)

        entry = look_by_id.get(sheet_id)
        if look is not None and entry is None:
            defects.append(_defect("visual_look_missing", sheet_id, "This sheet has no look record."))
        elif entry is not None:
            if entry.get("numerals_match_master") is not True:
                defects.append(
                    _defect(
                        "numeral_look_failed",
                        sheet_id,
                        "Numerals were not confirmed against the parts master.",
                    )
                )
            if stats["black_on_white"] is False and entry.get("black_on_white_seen") is True:
                defects.append(
                    _defect(
                        "look_disagrees_with_pixels",
                        sheet_id,
                        "The look record calls the sheet black-on-white, but the pixels are not.",
                    )
                )
            seen = entry.get("relationships_seen") or []
            if isinstance(seen, str):
                seen = [seen]
            for rel_id in rel_ids_by_sheet.get(sheet_id, []):
                if rel_id not in seen:
                    defects.append(
                        _defect(
                            "relationship_not_seen",
                            sheet_id,
                            f"Relationship '{rel_id}' is not recorded as visible on {sheet_id}.",
                        )
                    )

    if any(item["code"] in {"checksum_mismatch", "not_black_on_white", "blank_sheet", "image_unreadable"} for item in defects):
        defects.append(
            _defect("set_restart", "", "A failed sheet restarts the whole set. Return to patent-drawings.")
        )

    return {
        "sheets": opened,
        "errors": defects,
        "error_count": len(defects),
        "result": "PASS" if not defects else "FAIL",
    }


def render_text(report: dict) -> str:
    lines = ["Sheet visual report", ""]
    for sheet in report["sheets"]:
        lines.append(
            f"- {sheet.get('id')}: opened={sheet.get('opened')} "
            f"black_on_white={sheet.get('black_on_white')} sha256_ok={sheet.get('sha256_ok')}"
        )
    lines.append("")
    if report["errors"]:
        lines.append(f"ERRORS ({report['error_count']})")
        for error in report["errors"]:
            lines.append(f"- [{error['code']}] {error['message']}")
        lines.append("")
        lines.append("Result: FAIL")
    else:
        lines.append("Result: PASS")
    return "\n".join(lines)


def emit(report: dict, fmt: str) -> None:
    if fmt in ("text", "both"):
        print(render_text(report))
    if fmt == "both":
        print("===JSON===")
    if fmt in ("json", "both"):
        print(json.dumps(report, ensure_ascii=False, indent=2))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Open patent sheets and check pixels, hashes, and relationships.")
    parser.add_argument("--drawings", required=True, type=Path)
    parser.add_argument("--look", type=Path)
    parser.add_argument("--format", choices=["text", "json", "both"], default="both")
    args = parser.parse_args(argv)
    if not args.drawings.is_dir():
        print(f"Drawings directory not found: {args.drawings}", file=sys.stderr)
        return 2
    look = None
    if args.look is not None:
        if not args.look.is_file():
            print(f"File not found: {args.look}", file=sys.stderr)
            return 2
        try:
            look = _load(args.look)
        except ValueError as exc:
            print(str(exc), file=sys.stderr)
            return 2
    try:
        report = analyze(args.drawings, look)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    emit(report, args.format)
    return 1 if report["errors"] else 0


if __name__ == "__main__":
    sys.exit(main())
