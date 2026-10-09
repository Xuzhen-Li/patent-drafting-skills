#!/usr/bin/env python3
"""Copy existing drafts into a read-only folder and score which stages are real.

Copied files are mode 0444. A second copy does not overwrite. Junk names
such as .DS_Store are ignored. The score never closes a human gate. A
filename that says "complete" is not evidence. Drawing images count as a
finished drawing stage only when parts_master.json is frozen and every PNG
matches sheet_manifest.json. visual_look.json is written later by the
consistency checker.

    intake_existing.py copy --source <dir> --incoming <project>/incoming
    intake_existing.py score --project <project>

Exit codes
    0  copy finished, or score printed
    2  a directory is missing or JSON in the project is invalid
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

JUNK = {".ds_store", "thumbs.db", "desktop.ini"}
PLACEHOLDERS = ("【待发明人确认】", "[INVENTOR TO CONFIRM]")
UNITY_READY = {"one-invention", "documented-combination"}

STAGES = (
    ("disclosure", "invention-disclosure-intake", ("00-disclosure/disclosure.md",)),
    ("eligibility", "patentability-screen", ("01-eligibility/screen.md",)),
    ("prior_art", "prior-art-search", ("02-prior-art/search_log.md", "02-prior-art/feature_matrix.csv")),
    ("inventive_points", "inventive-point-finder", ("03-inventive-points/inventive_points.md",)),
    ("claims", "claims-drafter", ("04-claims/claims.md",)),
    ("description", "description-writer", ("05-description/description.md",)),
    ("abstract", "abstract-writer", ("06-abstract/abstract.md",)),
    ("consistency", "consistency-checker", ("08-consistency/report.md",)),
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 16), b""):
            digest.update(chunk)
    return digest.hexdigest()


def copy_readonly(source: Path, incoming: Path) -> list[dict]:
    if not source.is_dir():
        raise FileNotFoundError(f"Source directory not found: {source}")
    incoming.mkdir(parents=True, exist_ok=True)
    records = []
    files = sorted(path for path in source.rglob("*") if path.is_file())
    for path in files:
        rel = path.relative_to(source)
        if path.name.lower() in JUNK or path.name.startswith("."):
            records.append({"path": str(rel), "status": "ignored-junk"})
            continue
        target = incoming / rel
        if target.exists():
            records.append({"path": str(rel), "status": "left-in-place"})
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(path.read_bytes())
        target.chmod(0o444)
        records.append({"path": str(rel), "status": "copied-readonly"})
    return records


def _real_text(path: Path) -> bool:
    if not path.is_file():
        return False
    if path.suffix.lower() == ".csv":
        lines = [line for line in path.read_text(encoding="utf-8", errors="replace").splitlines() if line.strip()]
        return len(lines) >= 2 and "," in lines[0]
    text = path.read_text(encoding="utf-8", errors="replace").strip()
    if len(text) < 80:
        return False
    body = text
    for token in PLACEHOLDERS:
        body = body.replace(token, "")
    body = re.sub(r"^#+\s+.*$", "", body, flags=re.MULTILINE)
    body = re.sub(r"\s+", "", body)
    return len(body) >= 40


def _gate_flags(text: str) -> dict[str, bool]:
    flags: dict[str, bool] = {}
    in_gates = False
    for raw in text.splitlines():
        if re.match(r"^gates:\s*$", raw):
            in_gates = True
            continue
        if not in_gates:
            continue
        match = re.match(
            r"^\s+(invention_lock|prior_art_review|inventive_point_lock|claim_set_lock|final_package):\s*(true|false)\s*$",
            raw,
        )
        if match:
            flags[match.group(1)] = match.group(2) == "true"
            continue
        if raw.strip() and not raw.startswith((" ", "\t", "#")):
            in_gates = False
    return flags


def _yaml_value(text: str, key: str) -> str:
    match = re.search(rf"^{key}:\s*(\S+)", text, flags=re.MULTILINE)
    return match.group(1) if match else ""


def _unity_ready(path: Path) -> bool:
    if not path.is_file():
        return False
    match = re.search(r"unity_decision:\s*([A-Za-z-]+)", path.read_text(encoding="utf-8", errors="replace"))
    return bool(match and match.group(1) in UNITY_READY)


def drawings_checked(project: Path) -> bool:
    """True when the drawing stage's own files exist and the PNG bytes match.

    visual_look.json is not required here. The consistency checker writes
    that record after these sheets exist, then opens the images.
    """
    drawings = project / "07-drawings"
    master_path = drawings / "parts_master.json"
    manifest_path = drawings / "sheet_manifest.json"
    if not master_path.is_file() or not manifest_path.is_file():
        return False
    try:
        master = json.loads(master_path.read_text(encoding="utf-8-sig"))
        manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid drawings JSON: {exc}") from exc
    if master.get("frozen") is not True:
        return False
    sheets = manifest.get("sheets") or []
    if not sheets:
        return False
    for sheet in sheets:
        if not isinstance(sheet, dict):
            return False
        image = drawings / str(sheet.get("image") or "")
        if not image.is_file():
            return False
        if sha256_file(image) != str(sheet.get("sha256") or "").lower():
            return False
    return True


def score_project(project: Path) -> dict:
    if not project.is_dir():
        raise FileNotFoundError(f"Project directory not found: {project}")
    yaml_path = project / "patent.yaml"
    yaml_text = yaml_path.read_text(encoding="utf-8-sig") if yaml_path.is_file() else ""
    flags = _gate_flags(yaml_text)
    drawings_mode = _yaml_value(yaml_text, "drawings") or "pending"
    stages = {}
    for stage_id, _skill, rels in STAGES:
        real = all(_real_text(project / rel) for rel in rels)
        stages[stage_id] = {"real": real, "files": list(rels)}
    checked = False
    if drawings_mode == "none":
        checked = True
    else:
        checked = drawings_checked(project)
    stages["drawings"] = {
        "real": checked,
        "files": ["07-drawings/parts_master.json", "07-drawings/sheet_manifest.json"],
        "mode": drawings_mode,
    }

    inconsistent = []
    if flags.get("invention_lock") and not stages["disclosure"]["real"]:
        inconsistent.append("invention_lock")
    if flags.get("prior_art_review") and not stages["prior_art"]["real"]:
        inconsistent.append("prior_art_review")
    points = project / "03-inventive-points" / "inventive_points.md"
    if flags.get("inventive_point_lock") and (not stages["inventive_points"]["real"] or not _unity_ready(points)):
        inconsistent.append("inventive_point_lock")
    if flags.get("claim_set_lock") and not stages["claims"]["real"]:
        inconsistent.append("claim_set_lock")
    if flags.get("final_package") and not any((project / "09-package").glob("*.docx")):
        inconsistent.append("final_package")

    if not stages["disclosure"]["real"] or not flags.get("invention_lock"):
        earliest = "invention-disclosure-intake"
    elif not stages["eligibility"]["real"]:
        earliest = "patentability-screen"
    elif not stages["prior_art"]["real"] or not flags.get("prior_art_review"):
        earliest = "prior-art-search"
    elif not stages["inventive_points"]["real"] or not flags.get("inventive_point_lock") or not _unity_ready(points):
        earliest = "inventive-point-finder"
    elif not stages["claims"]["real"] or not flags.get("claim_set_lock"):
        earliest = "claims-drafter"
    elif not stages["description"]["real"]:
        earliest = "description-writer"
    elif not stages["abstract"]["real"]:
        earliest = "abstract-writer"
    elif drawings_mode != "none" and not checked:
        earliest = "patent-drawings"
    elif not stages["consistency"]["real"]:
        earliest = "consistency-checker"
    elif not flags.get("final_package"):
        earliest = "patent-docx-export"
    else:
        earliest = "none"

    incoming = project / "incoming"
    incoming_names = []
    if incoming.is_dir():
        incoming_names = [
            str(path.relative_to(incoming))
            for path in sorted(incoming.rglob("*"))
            if path.is_file() and not path.name.startswith(".")
        ]
    return {
        "earliest_missing": earliest,
        "gates_inconsistent": inconsistent,
        "stages": stages,
        "drawings_checked": checked,
        "incoming_files": incoming_names,
        "note": "This score does not close a gate. A filename is not proof that a stage was reviewed.",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Import existing drafts read-only and score real stage files.")
    sub = parser.add_subparsers(dest="command", required=True)
    copy = sub.add_parser("copy")
    copy.add_argument("--source", required=True, type=Path)
    copy.add_argument("--incoming", required=True, type=Path)
    score = sub.add_parser("score")
    score.add_argument("--project", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        if args.command == "copy":
            records = copy_readonly(args.source, args.incoming)
            print(json.dumps({"copied": records}, ensure_ascii=False, indent=2))
            return 0
        payload = score_project(args.project)
    except FileNotFoundError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    if args.command == "score":
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
