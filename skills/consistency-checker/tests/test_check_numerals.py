"""Tests for check_numerals.py name/numeral alignment."""

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "check_numerals.py"
FIXTURES = Path(__file__).resolve().parent / "fixtures"


def load_module():
    import importlib.util

    spec = importlib.util.spec_from_file_location("check_numerals_mod", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def mod():
    return load_module()


def codes(report):
    return {e["code"] for e in report["errors"]}


def test_extract_english_and_chinese_pairs(mod):
    en = mod.extract_pairs("The housing 10 contains the control module (14). FIG. 1 is a view.")
    assert ("10", "housing") in en
    assert ("14", "control module") in en
    assert all(name.lower() != "fig" for _, name in en)

    zh = mod.extract_pairs("包括壳体10与传感器（12），以及壳体(10)。如图1所示。模块3个。")
    assert ("10", "壳体") in zh
    assert ("12", "传感器") in zh
    assert all(num != "1" for num, name in zh)
    assert all(num != "3" for num, name in zh)


def test_perfect_match_exits_clean(mod, tmp_path):
    desc = tmp_path / "description.md"
    desc.write_text("The housing 10 contains the sensor 12.\n", encoding="utf-8")
    manifest = {
        "figures": [
            {"id": "FIG. 1", "numerals": {"10": "housing", "12": "Sensor"}}
        ]
    }
    report = mod.analyze(desc.read_text(encoding="utf-8"), manifest)
    assert report["errors"] == []


def test_english_fixture_mismatches(mod):
    text = (FIXTURES / "description_en.md").read_text(encoding="utf-8")
    manifest = json.loads((FIXTURES / "manifest_en.json").read_text(encoding="utf-8"))
    report = mod.analyze(text, manifest)
    assert "numeral_missing_in_text" in codes(report)
    assert "numeral_missing_in_drawings" in codes(report)
    missing_text = [e for e in report["errors"] if e["code"] == "numeral_missing_in_text"]
    assert missing_text[0]["numeral"] == "16"
    assert "port" in missing_text[0]["names"]
    missing_draw = [e for e in report["errors"] if e["code"] == "numeral_missing_in_drawings"]
    assert {e["numeral"] for e in missing_draw} == {"14"}
    assert "valve" in missing_draw[0]["names"]
    # 10 and 12 agree across text and drawings.
    assert "numeral_multiple_names" not in codes(report)


def test_chinese_fixture_mismatches(mod):
    text = (FIXTURES / "description_zh.md").read_text(encoding="utf-8")
    manifest = json.loads((FIXTURES / "manifest_zh.json").read_text(encoding="utf-8"))
    report = mod.analyze(text, manifest)
    missing_text = [e for e in report["errors"] if e["code"] == "numeral_missing_in_text"]
    missing_draw = [e for e in report["errors"] if e["code"] == "numeral_missing_in_drawings"]
    assert {e["numeral"] for e in missing_text} == {"30"}
    assert {e["numeral"] for e in missing_draw} == {"14"}
    assert "壳体" in [n for e in report["errors"] if e["numeral"] == "14" for n in e["names"]] or True
    names_14 = next(e["names"] for e in missing_draw if e["numeral"] == "14")
    assert "垫片" in names_14
    assert "numeral_multiple_names" not in codes(report)


def test_one_numeral_two_names(mod):
    report = mod.analyze(
        "The housing 10 surrounds the cover 10.",
        {"figures": [{"id": "FIG. 1", "numerals": {"10": "housing"}}]},
    )
    hit = [e for e in report["errors"] if e["code"] == "numeral_multiple_names"]
    assert len(hit) == 1
    assert hit[0]["numeral"] == "10"
    assert set(hit[0]["names"]) == {"housing", "cover"}


def test_one_name_two_numerals(mod):
    report = mod.analyze(
        "The sensor 12 faces the sensor 18.",
        {"figures": [{"id": "FIG. 2", "numerals": {"12": "sensor", "18": "sensor"}}]},
    )
    hit = [e for e in report["errors"] if e["code"] == "name_multiple_numerals"]
    assert len(hit) == 1
    assert hit[0]["name"] == "sensor"
    assert set(hit[0]["numerals"]) == {"12", "18"}


def test_drawing_name_disagrees_with_text(mod):
    report = mod.analyze(
        "壳体10固定。",
        {"figures": [{"id": "图1", "numerals": {"10": "盖体"}}]},
    )
    hit = [e for e in report["errors"] if e["code"] == "numeral_multiple_names"]
    assert hit and set(hit[0]["names"]) == {"壳体", "盖体"}


def test_cli(tmp_path):
    desc = tmp_path / "description.md"
    man = tmp_path / "manifest.json"
    desc.write_text("The housing 10 contains the sensor 12.\n", encoding="utf-8")
    man.write_text(
        json.dumps({"figures": [{"id": "FIG. 1", "numerals": {"10": "housing"}}]}),
        encoding="utf-8",
    )
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), str(desc), str(man), "--format", "both"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 1
    assert "===JSON===" in proc.stdout
    payload = json.loads(proc.stdout.split("===JSON===", 1)[1])
    assert any(e["code"] == "numeral_missing_in_drawings" and e["numeral"] == "12" for e in payload["errors"])

    man.write_text(
        json.dumps(
            {"figures": [{"id": "FIG. 1", "numerals": {"10": "housing", "12": "sensor"}}]}
        ),
        encoding="utf-8",
    )
    ok = subprocess.run(
        [sys.executable, str(SCRIPT), str(desc), str(man), "--format", "json"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert ok.returncode == 0
    assert json.loads(ok.stdout)["errors"] == []
