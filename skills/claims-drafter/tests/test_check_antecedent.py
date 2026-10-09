"""Tests for check_antecedent.py. Fixtures include sound and broken claims."""

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "check_antecedent.py"
FIXTURES = Path(__file__).resolve().parent / "fixtures"


def load_module():
    import importlib.util

    spec = importlib.util.spec_from_file_location("check_antecedent_mod", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def mod():
    return load_module()


def codes(report):
    return [(e["code"], e["claim"]) for e in report["errors"]]


def by_code(report, code, claim=None):
    out = [e for e in report["errors"] if e["code"] == code]
    if claim is not None:
        out = [e for e in out if e["claim"] == claim]
    return out


def test_parse_fullwidth_period(mod):
    claims = mod.parse_claims("1．一种装置，包括壳体。\n\n2．根据权利要求1所述的装置，包括盖体。\n")
    assert [c["number"] for c in claims] == [1, 2]
    assert claims[0]["text"].startswith("一种装置")


def test_does_not_split_decimal_line(mod):
    claims = mod.parse_claims("1. A device comprising a gap of 1.5 mm.\n")
    assert len(claims) == 1
    assert "1.5" in claims[0]["text"]


def test_english_dependency_patterns(mod):
    deps, alt = mod.extract_dependencies(
        "The device according to claim 1 or 2, wherein the housing is metal."
    )
    assert deps == [1, 2]
    assert alt is True

    deps, alt = mod.extract_dependencies(
        "The device according to claims 1 and 2, wherein the housing is metal."
    )
    assert deps == [1, 2]
    assert alt is False

    deps, alt = mod.extract_dependencies(
        "The device as claimed in claim 1 or claim 2, wherein the housing is metal."
    )
    assert deps == [1, 2]
    assert alt is True

    deps, alt = mod.extract_dependencies(
        "The device of any one of claims 1 to 3, wherein the housing is metal."
    )
    assert deps == [1, 2, 3]
    assert alt is True

    deps, alt = mod.extract_dependencies("A device comprising a housing.")
    assert deps == []
    assert alt is None


def test_chinese_dependency_patterns(mod):
    deps, alt = mod.extract_dependencies("根据权利要求1所述的装置，包括盖体。")
    assert deps == [1]
    assert alt is None

    deps, alt = mod.extract_dependencies("根据权利要求1或2所述的装置。")
    assert deps == [1, 2]
    assert alt is True

    deps, alt = mod.extract_dependencies("如权利要求1-3任一项所述的装置。")
    assert deps == [1, 2, 3]
    assert alt is True

    deps, alt = mod.extract_dependencies("根据权利要求1至3中任一项所述的装置。")
    assert deps == [1, 2, 3]
    assert alt is True

    deps, alt = mod.extract_dependencies("根据权利要求1、2或3所述的装置。")
    assert deps == [1, 2, 3]
    assert alt is True

    deps, alt = mod.extract_dependencies("根据权利要求1和2所述的装置。")
    assert deps == [1, 2]
    assert alt is False

    deps, alt = mod.extract_dependencies("根据权利要求1、2所述的装置。")
    assert deps == [1, 2]
    assert alt is False


def test_en_ok_fixture(mod):
    report = mod.analyze_path(FIXTURES / "en_ok.md", lang="en")
    assert report["errors"] == []
    assert report["claim_count"] == 3
    claim3 = report["claims"][2]
    assert claim3["dependencies"] == [1, 2]
    assert claim3["alternative"] is True
    assert claim3["multiple_dependent"] is True


def test_zh_ok_fixture(mod):
    report = mod.analyze_path(FIXTURES / "zh_ok.md", lang="zh")
    assert report["errors"] == []
    assert report["claim_count"] == 4
    assert report["claims"][2]["dependencies"] == [1, 2]
    assert report["claims"][2]["alternative"] is True


def test_en_broken_fixture(mod):
    report = mod.analyze_path(FIXTURES / "en_broken.md", lang="en")
    assert report["error_count"] == 5
    assert ("forward_reference", 2) in codes(report)
    assert by_code(report, "forward_reference", 2)[0]["refs"] == [3]
    sensor = by_code(report, "missing_antecedent", 2)
    assert {e["phrase"] for e in sensor} == {"sensor"}
    assert by_code(report, "multiple_dependent_not_alternative", 4)[0]["refs"] == [1, 2]
    assert by_code(report, "multiple_dependent_basis", 5)[0]["parents"] == [4]
    assert by_code(report, "missing_claim", 6)[0]["refs"] == [9]


def test_zh_broken_fixture(mod):
    report = mod.analyze_path(FIXTURES / "zh_broken.md", lang="zh")
    assert ("forward_reference", 2) in codes(report)
    assert by_code(report, "forward_reference", 2)[0]["refs"] == [3]
    assert {e["phrase"] for e in by_code(report, "missing_antecedent", 2)} == {"传感器"}
    assert by_code(report, "multiple_dependent_not_alternative", 4)[0]["refs"] == [1, 2]
    assert by_code(report, "multiple_dependent_basis", 5)[0]["parents"] == [4]
    assert by_code(report, "missing_claim", 6)[0]["refs"] == [9]
    assert by_code(report, "forward_reference", 7)[0]["refs"] == [7]
    basis7 = by_code(report, "multiple_dependent_basis", 7)[0]["parents"]
    assert basis7 == [4, 5]
    # Sound nouns in claim 7 must not be flagged: 壳体 and 传感装置 are in the ancestor chain.
    assert by_code(report, "missing_antecedent", 7) == []
    assert report["error_count"] == 7


def test_auto_lang_and_limitations(mod):
    en = mod.analyze_path(FIXTURES / "en_ok.md", lang="auto")
    zh = mod.analyze_path(FIXTURES / "zh_ok.md", lang="auto")
    assert en["lang"] == "en"
    assert zh["lang"] == "zh"
    assert en["limitations"]
    assert zh["errors"] == []


def test_duplicate_claim_number(mod):
    text = "1. A device comprising a housing.\n\n1. The device according to claim 1, wherein the housing is metal.\n"
    report = mod.analyze_text(text, lang="en")
    assert any(e["code"] == "duplicate_claim" for e in report["errors"])


def test_no_claims(mod):
    report = mod.analyze_text("This file has no numbered claims.\n", lang="en")
    assert any(e["code"] == "no_claims" for e in report["errors"])


def test_cli_exit_codes_and_json():
    ok = subprocess.run(
        [sys.executable, str(SCRIPT), str(FIXTURES / "zh_ok.md"), "--lang", "zh", "--format", "json"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert ok.returncode == 0
    payload = json.loads(ok.stdout)
    assert payload["error_count"] == 0

    bad = subprocess.run(
        [sys.executable, str(SCRIPT), str(FIXTURES / "en_broken.md"), "--lang", "en", "--format", "both"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert bad.returncode == 1
    assert "===JSON===" in bad.stdout
    human, raw = bad.stdout.split("===JSON===", 1)
    assert "forward_reference" in human or "Claim 2" in human
    payload = json.loads(raw)
    assert payload["error_count"] == 5
    assert payload["limitations"]
