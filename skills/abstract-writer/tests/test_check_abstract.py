"""Tests for check_abstract.py counting rules, warnings, and exit codes."""

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "check_abstract.py"
FIXTURES = Path(__file__).resolve().parent / "fixtures"


def load_module():
    import importlib.util

    spec = importlib.util.spec_from_file_location("check_abstract_mod", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def mod():
    return load_module()


def test_zh_counting_rule_includes_punctuation_excludes_whitespace(mod):
    assert mod.count_zh("甲，乙") == 3
    assert mod.count_zh("甲 乙\n") == 2
    assert mod.count_zh("甲\u3000乙") == 2
    assert "punctuation" in mod.COUNTING_RULE_ZH.lower()
    assert "whitespace" in mod.COUNTING_RULE_ZH.lower()


def test_en_word_count(mod):
    assert mod.count_en("one two three") == 3
    assert mod.count_en("one\ntwo  three") == 3
    assert mod.count_en("state-of-the-art sensor") == 2
    assert "150" in mod.COUNTING_RULE_EN


def test_zh_limits(mod, tmp_path):
    exact = tmp_path / "exact.md"
    exact.write_text("测" * 300, encoding="utf-8")
    report = mod.analyze_path(exact, lang="zh")
    assert report["count"] == 300
    assert report["limit"] == 300
    assert report["unit"] == "characters"
    assert report["over_limit"] is False
    assert report["errors"] == []

    over = tmp_path / "over.md"
    over.write_text("测" * 301, encoding="utf-8")
    report = mod.analyze_path(over, lang="zh")
    assert report["count"] == 301
    assert report["over_limit"] is True
    assert report["errors"][0]["code"] == "over_limit"


def test_en_limits(mod, tmp_path):
    exact = tmp_path / "exact.md"
    exact.write_text(" ".join(["word"] * 150), encoding="utf-8")
    report = mod.analyze_path(exact, lang="en")
    assert report["count"] == 150
    assert report["limit"] == 150
    assert report["unit"] == "words"
    assert report["errors"] == []

    over = tmp_path / "over.md"
    over.write_text(" ".join(["word"] * 151), encoding="utf-8")
    report = mod.analyze_path(over, lang="en")
    assert report["over_limit"] is True
    assert report["errors"][0]["code"] == "over_limit"


def test_zh_warnings_do_not_replace_length_error(mod):
    text = "其特征在于" + ("最佳" * 150)
    report = mod.analyze_text(text, lang="zh")
    assert report["over_limit"] is True
    codes = {w["code"] for w in report["warnings"]}
    assert "claim_language" in codes
    assert "advertising_language" in codes


def test_fixture_exit_classes(mod):
    short = mod.analyze_path(FIXTURES / "zh_short.md", lang="auto")
    assert short["lang"] == "zh"
    assert short["errors"] == []
    assert short["warnings"] == []

    claimish = mod.analyze_path(FIXTURES / "zh_claimish.md", lang="zh")
    assert claimish["errors"] == []
    assert {w["code"] for w in claimish["warnings"]} >= {"claim_language", "advertising_language"}
    assert any(w["phrase"] == "其特征在于" for w in claimish["warnings"])
    assert any(w["phrase"] == "最佳" for w in claimish["warnings"])
    assert any(w["phrase"] == "革命性" for w in claimish["warnings"])

    en = mod.analyze_path(FIXTURES / "en_short.md", lang="auto")
    assert en["lang"] == "en"
    assert en["warnings"] == []

    en_bad = mod.analyze_path(FIXTURES / "en_claimish.md", lang="en")
    phrases = {w["phrase"].lower() for w in en_bad["warnings"]}
    assert "characterized in that" in phrases
    assert "revolutionary" in phrases
    assert "unique" in phrases


def test_cli_exit_codes():
    ok = subprocess.run(
        [sys.executable, str(SCRIPT), str(FIXTURES / "en_short.md"), "--lang", "en", "--format", "json"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert ok.returncode == 0
    assert json.loads(ok.stdout)["count"] > 0

    warn = subprocess.run(
        [sys.executable, str(SCRIPT), str(FIXTURES / "zh_claimish.md"), "--lang", "zh", "--format", "both"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert warn.returncode == 2
    assert "===JSON===" in warn.stdout
    payload = json.loads(warn.stdout.split("===JSON===", 1)[1])
    assert payload["warnings"]
    assert payload["errors"] == []

    over = subprocess.run(
        [sys.executable, str(SCRIPT), str(FIXTURES / "zh_short.md"), "--lang", "zh", "--format", "json"],
        capture_output=True,
        text=True,
        check=False,
    )
    # Control: short file passes. Over-limit is covered by a generated file below.
    assert over.returncode == 0


def test_cli_over_limit_exits_1(tmp_path):
    path = tmp_path / "long.md"
    path.write_text("word " * 151, encoding="utf-8")
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), str(path), "--lang", "en", "--format", "json"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 1
    payload = json.loads(proc.stdout)
    assert payload["over_limit"] is True
    assert payload["counting_rule"]
