#!/usr/bin/env python3
"""Hash formal drawing sheets and reject sources that are not editable.

A formal sheet is a PNG exported from an editable source. The source kind
must be one of graphviz, mermaid, drawio, svg, or matplotlib. Image-model
bitmaps, traced art, invented spectra, and invented chemical structures
are rejected and are not given a passing checksum.

parts_master.json must already be frozen (frozen: true) and must list at
least one part or step. Later views derive from that master; this script
does not add parts.

    sheet_checksums.py build --drawings <07-drawings> --plan plan.json --out sheet_manifest.json
    sheet_checksums.py verify --drawings <07-drawings> --manifest sheet_manifest.json

Exit codes
    0  manifest written, or verify found no mismatch
    1  a sheet was rejected or a checksum did not match
    2  a required file is missing or JSON is invalid
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ALLOWED_KINDS = {
    ".dot": "graphviz",
    ".gv": "graphviz",
    ".mmd": "mermaid",
    ".mermaid": "mermaid",
    ".drawio": "drawio",
    ".svg": "svg",
    ".py": "matplotlib",
}

FORBIDDEN_KINDS = {
    "image_model",
    "traced",
    "traced_art",
    "invented_spectrum",
    "invented_structure",
}

CURVE_CONTENT = {"spectrum", "gel", "curve"}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 16), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _norm(value: object) -> str:
    return str(value or "").strip().lower().replace("-", "_")


def _load_json(path: Path) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON in {path.name}: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError(f"{path.name} must be a JSON object")
    return data


def master_problems(data: dict) -> list[dict]:
    problems: list[dict] = []
    if data.get("frozen") is not True:
        problems.append(
            {
                "code": "master_not_frozen",
                "sheet": "",
                "message": "parts_master.json must be frozen before any formal sheet is hashed.",
            }
        )
    parts = data.get("parts")
    if not isinstance(parts, list) or not parts:
        problems.append(
            {
                "code": "master_empty",
                "sheet": "",
                "message": "parts_master.json needs a non-empty parts list.",
            }
        )
        return problems
    for index, part in enumerate(parts):
        if not isinstance(part, dict) or not str(part.get("id", "")).strip() or not str(part.get("name", "")).strip():
            problems.append(
                {
                    "code": "master_part_incomplete",
                    "sheet": "",
                    "message": f"parts[{index}] needs an id and a name.",
                }
            )
    return problems


def _problem(code: str, sheet_id: str, message: str) -> dict:
    return {"code": code, "sheet": sheet_id, "message": message}


def evaluate_sheet(drawings: Path, sheet: dict) -> tuple[dict | None, list[dict]]:
    sheet_id = str(sheet.get("id", "")).strip()
    problems: list[dict] = []
    if not sheet_id:
        problems.append(_problem("missing_sheet_id", "", "Each sheet needs an id."))
        return None, problems

    kind = _norm(sheet.get("source_kind"))
    if kind in FORBIDDEN_KINDS:
        problems.append(
            _problem(
                "forbidden_source",
                sheet_id,
                f"Source kind '{kind}' cannot become a formal sheet.",
            )
        )
        return None, problems

    content = _norm(sheet.get("content") or "diagram")
    if content in CURVE_CONTENT:
        data_name = str(sheet.get("data_file") or "").strip()
        data_path = drawings / data_name if data_name else None
        if data_path is None or not data_path.is_file():
            problems.append(
                _problem(
                    "invented_spectrum",
                    sheet_id,
                    "A spectrum, gel, or curve needs the inventor's data file. None was found.",
                )
            )
            return None, problems

    if content == "chemical_structure":
        structure_name = str(sheet.get("structure_source") or "").strip()
        structure_path = drawings / structure_name if structure_name else None
        if structure_path is None or not structure_path.is_file():
            problems.append(
                _problem(
                    "invented_structure",
                    sheet_id,
                    "A chemical structure needs the inventor's structure file, not an image model.",
                )
            )
            return None, problems

    image_name = str(sheet.get("image") or "").strip()
    source_name = str(sheet.get("source") or "").strip()
    image_path = drawings / image_name if image_name else None
    source_path = drawings / source_name if source_name else None
    if image_path is None or not image_path.is_file():
        problems.append(_problem("missing_image", sheet_id, "The PNG sheet is missing."))
        return None, problems
    if image_path.suffix.lower() != ".png":
        problems.append(_problem("png_sheet_required", sheet_id, "The formal sheet file must be a PNG."))
        return None, problems
    if source_path is None or not source_path.is_file():
        problems.append(
            _problem(
                "missing_editable_source",
                sheet_id,
                "A formal sheet needs an editable source next to the PNG.",
            )
        )
        return None, problems

    expected_kind = ALLOWED_KINDS.get(source_path.suffix.lower())
    if expected_kind is None:
        problems.append(
            _problem(
                "source_not_editable",
                sheet_id,
                f"Source suffix '{source_path.suffix}' is not an editable diagram or vector source.",
            )
        )
        return None, problems
    if kind and kind != expected_kind:
        problems.append(
            _problem(
                "source_kind_mismatch",
                sheet_id,
                f"Declared kind '{kind}' does not match the source file ({expected_kind}).",
            )
        )
        return None, problems

    record = {
        "id": sheet_id,
        "image": image_name,
        "sha256": sha256_file(image_path),
        "source": source_name,
        "source_kind": expected_kind,
        "source_sha256": sha256_file(source_path),
        "content": content,
    }
    if content in CURVE_CONTENT:
        record["data_file"] = str(sheet.get("data_file"))
    if content == "chemical_structure":
        record["structure_source"] = str(sheet.get("structure_source"))
    return record, problems


def build_manifest(drawings: Path, plan: dict) -> tuple[dict | None, list[dict]]:
    master_path = drawings / "parts_master.json"
    if not master_path.is_file():
        return None, [_problem("master_missing", "", "parts_master.json is missing.")]
    try:
        master = _load_json(master_path)
    except ValueError as exc:
        return None, [_problem("master_invalid", "", str(exc))]
    problems = master_problems(master)
    if problems:
        return None, problems

    sheets = plan.get("sheets")
    if not isinstance(sheets, list) or not sheets:
        return None, [_problem("plan_empty", "", "The sheet plan needs a non-empty sheets list.")]

    records = []
    for sheet in sheets:
        if not isinstance(sheet, dict):
            problems.append(_problem("plan_sheet_invalid", "", "Each plan sheet must be an object."))
            continue
        record, sheet_problems = evaluate_sheet(drawings, sheet)
        problems.extend(sheet_problems)
        if record is not None:
            records.append(record)
    if problems:
        return None, problems
    return {"sheets": records}, []


def verify_manifest(drawings: Path, manifest: dict) -> list[dict]:
    problems: list[dict] = []
    sheets = manifest.get("sheets")
    if not isinstance(sheets, list) or not sheets:
        return [_problem("manifest_empty", "", "sheet_manifest.json has no sheets.")]
    for sheet in sheets:
        if not isinstance(sheet, dict):
            problems.append(_problem("manifest_sheet_invalid", "", "A manifest sheet is not an object."))
            continue
        sheet_id = str(sheet.get("id", ""))
        image_name = str(sheet.get("image") or "")
        image_path = drawings / image_name
        expected = str(sheet.get("sha256") or "").lower()
        if not image_path.is_file():
            problems.append(_problem("missing_image", sheet_id, f"Missing sheet image {image_name}."))
        elif sha256_file(image_path) != expected:
            problems.append(
                _problem(
                    "checksum_mismatch",
                    sheet_id,
                    f"{image_name} no longer matches the stored sha256. Rebuild the whole set.",
                )
            )
        source_name = str(sheet.get("source") or "")
        source_path = drawings / source_name if source_name else None
        source_expected = str(sheet.get("source_sha256") or "").lower()
        if source_path is None or not source_path.is_file():
            problems.append(_problem("missing_editable_source", sheet_id, "Editable source is missing."))
        elif source_expected and sha256_file(source_path) != source_expected:
            problems.append(
                _problem(
                    "source_checksum_mismatch",
                    sheet_id,
                    f"{source_name} changed after the sheet was hashed. Rebuild the whole set.",
                )
            )
        if _norm(sheet.get("source_kind")) in FORBIDDEN_KINDS:
            problems.append(_problem("forbidden_source", sheet_id, "Manifest lists a forbidden source kind."))
    if problems:
        problems.append(
            _problem(
                "set_restart",
                "",
                "One changed or rejected sheet restarts the whole set. Do not pass the other sheets.",
            )
        )
    return problems


def _emit(payload: dict) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build or verify formal-sheet sha256 manifests.")
    sub = parser.add_subparsers(dest="command", required=True)

    build = sub.add_parser("build")
    build.add_argument("--drawings", required=True, type=Path)
    build.add_argument("--plan", required=True, type=Path)
    build.add_argument("--out", required=True, type=Path)

    verify = sub.add_parser("verify")
    verify.add_argument("--drawings", required=True, type=Path)
    verify.add_argument("--manifest", required=True, type=Path)

    args = parser.parse_args(argv)
    if not args.drawings.is_dir():
        print(f"Drawings directory not found: {args.drawings}", file=sys.stderr)
        return 2

    if args.command == "build":
        if not args.plan.is_file():
            print(f"File not found: {args.plan}", file=sys.stderr)
            return 2
        try:
            plan = _load_json(args.plan)
        except ValueError as exc:
            print(str(exc), file=sys.stderr)
            return 2
        manifest, problems = build_manifest(args.drawings, plan)
        if problems:
            _emit({"errors": problems, "error_count": len(problems)})
            return 1
        args.out.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        _emit(manifest)
        return 0

    if not args.manifest.is_file():
        print(f"File not found: {args.manifest}", file=sys.stderr)
        return 2
    try:
        manifest = _load_json(args.manifest)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    problems = verify_manifest(args.drawings, manifest)
    _emit({"errors": problems, "error_count": len(problems)})
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
