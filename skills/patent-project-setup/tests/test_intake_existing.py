"""Existing-draft intake: read-only copy and stage score."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import stat
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "intake_existing.py"


def load_module():
    spec = importlib.util.spec_from_file_location("intake_existing_mod", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


LONG = (
    "The housing encloses a sensor that samples temperature on every cycle recorded in the lab notebook. "
    "This sentence is long enough to count as a real draft rather than a placeholder title.\n"
)


def write(path: Path, text: str | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text if text is not None else LONG, encoding="utf-8")


def yaml_text(locks: dict, drawings: str = "planned") -> str:
    lines = ["title: Sensor", "jurisdiction: US", f"drawings: {drawings}", "gates:"]
    for name in (
        "invention_lock",
        "prior_art_review",
        "inventive_point_lock",
        "claim_set_lock",
        "final_package",
    ):
        lines.append(f"  {name}: {'true' if locks.get(name) else 'false'}")
    return "\n".join(lines) + "\n"


def test_copy_is_readonly_and_does_not_overwrite(tmp_path):
    mod = load_module()
    source = tmp_path / "drop"
    write(source / "notes.md", LONG)
    (source / ".DS_Store").write_bytes(b"junk")
    incoming = tmp_path / "project" / "incoming"
    first = mod.copy_readonly(source, incoming)
    assert {row["status"] for row in first} == {"copied-readonly", "ignored-junk"}
    copied = incoming / "notes.md"
    assert stat.S_IMODE(copied.stat().st_mode) & 0o222 == 0
    copied.chmod(0o644)
    copied.write_text("original copy\n" + LONG, encoding="utf-8")
    copied.chmod(0o444)
    write(source / "notes.md", "rewritten source that must not replace the drop\n" + LONG)
    second = mod.copy_readonly(source, incoming)
    notes = next(row for row in second if row["path"] == "notes.md")
    assert notes["status"] == "left-in-place"
    assert "original copy" in copied.read_text(encoding="utf-8")


def test_later_claims_do_not_skip_an_open_lock(tmp_path):
    mod = load_module()
    project = tmp_path / "project"
    write(project / "patent.yaml", yaml_text({}))
    write(project / "00-disclosure" / "disclosure.md")
    write(project / "04-claims" / "claims.md")
    write(project / "incoming" / "complete.md", "complete is only a filename\n")
    score = mod.score_project(project)
    assert score["earliest_missing"] == "invention-disclosure-intake"
    assert score["stages"]["claims"]["real"] is True
    assert "complete.md" in score["incoming_files"]
    assert score["stages"]["disclosure"]["real"] is True


def _filled_through_abstract(project: Path) -> None:
    locks = {
        "invention_lock": True,
        "prior_art_review": True,
        "inventive_point_lock": True,
        "claim_set_lock": True,
    }
    write(project / "patent.yaml", yaml_text(locks))
    write(project / "00-disclosure" / "disclosure.md")
    write(project / "01-eligibility" / "screen.md")
    write(project / "02-prior-art" / "search_log.md")
    write(project / "02-prior-art" / "feature_matrix.csv", "feature_id,feature_text,ours\nF1,housing,yes\n")
    write(
        project / "03-inventive-points" / "inventive_points.md",
        LONG + "\nunity_decision: one-invention\n",
    )
    write(project / "04-claims" / "claims.md")
    write(project / "05-description" / "description.md")
    write(project / "06-abstract" / "abstract.md")


def test_unchecked_drawings_are_not_finished(tmp_path):
    mod = load_module()
    project = tmp_path / "project"
    _filled_through_abstract(project)
    write(project / "07-drawings" / "figure_list.md")
    (project / "07-drawings" / "fig1.png").write_bytes(b"\x89PNG-not-reviewed")
    score = mod.score_project(project)
    assert score["drawings_checked"] is False
    assert score["earliest_missing"] == "patent-drawings"


def test_checksummed_sheets_without_look_go_to_consistency(tmp_path):
    mod = load_module()
    project = tmp_path / "project"
    _filled_through_abstract(project)
    drawings = project / "07-drawings"
    drawings.mkdir(parents=True)
    png = b"\x89PNG\r\n\x1a\nchecked"
    (drawings / "fig1.png").write_bytes(png)
    digest = hashlib.sha256(png).hexdigest()
    write(
        drawings / "parts_master.json",
        json.dumps({"frozen": True, "parts": [], "relationships": []}),
    )
    write(
        drawings / "sheet_manifest.json",
        json.dumps({"sheets": [{"id": "FIG. 1", "image": "fig1.png", "sha256": digest}]}),
    )
    score = mod.score_project(project)
    assert score["drawings_checked"] is True
    assert score["earliest_missing"] == "consistency-checker"
    assert not (drawings / "visual_look.json").exists()


def test_lock_without_a_real_file_is_inconsistent(tmp_path):
    mod = load_module()
    project = tmp_path / "project"
    write(project / "patent.yaml", yaml_text({"invention_lock": True, "inventive_point_lock": True}))
    write(project / "00-disclosure" / "disclosure.md", "【待发明人确认】\n")
    write(project / "03-inventive-points" / "inventive_points.md", LONG)
    score = mod.score_project(project)
    assert "invention_lock" in score["gates_inconsistent"]
    assert "inventive_point_lock" in score["gates_inconsistent"]
    assert score["earliest_missing"] == "invention-disclosure-intake"


def test_drawings_none_can_move_past_figures(tmp_path):
    mod = load_module()
    project = tmp_path / "project"
    locks = {
        "invention_lock": True,
        "prior_art_review": True,
        "inventive_point_lock": True,
        "claim_set_lock": True,
    }
    write(project / "patent.yaml", yaml_text(locks, drawings="none"))
    write(project / "00-disclosure" / "disclosure.md")
    write(project / "01-eligibility" / "screen.md")
    write(project / "02-prior-art" / "search_log.md")
    write(project / "02-prior-art" / "feature_matrix.csv", "feature_id,feature_text,ours\nF1,housing,yes\n")
    write(
        project / "03-inventive-points" / "inventive_points.md",
        LONG + "\nunity_decision: documented-combination\n",
    )
    write(project / "04-claims" / "claims.md")
    write(project / "05-description" / "description.md")
    write(project / "06-abstract" / "abstract.md")
    score = mod.score_project(project)
    assert score["earliest_missing"] == "consistency-checker"
    assert json.dumps(score)
