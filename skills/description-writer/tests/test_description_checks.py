"""Admission and added-matter scans."""

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(name):
    path = ROOT / "scripts" / name
    spec = importlib.util.spec_from_file_location(name.replace(".py", "_mod"), path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_admission_flags_unsourced_and_invention_as_known(tmp_path):
    mod = load("admission_scan.py")
    path = tmp_path / "description.md"
    path.write_text(
        "\n".join(
            [
                "# 技术领域",
                "本发明涉及传感器。",
                "# 背景技术",
                "众所周知，该问题一直存在。",
                "本发明的方案已被 CN1122333A 公开。",
                "对比文件 CN1122333A 公开了一种壳体。",
                "# 发明内容",
                "众所周知这句话不在背景里，不应被扫到。",
            ]
        ),
        encoding="utf-8",
    )
    report = mod.scan(path.read_text(encoding="utf-8"))
    assert report["flag_count"] == 2
    reasons = {flag["text"]: flag["reasons"] for flag in report["flags"]}
    assert "known_without_source" in reasons["众所周知，该问题一直存在。"]
    assert "attributes_the_invention_to_the_prior_art" in reasons["本发明的方案已被 CN1122333A 公开。"]
    assert mod.main([str(path)]) == 1


def test_admission_passes_a_cited_background(tmp_path):
    mod = load("admission_scan.py")
    path = tmp_path / "description.md"
    path.write_text(
        "# Background\n\nCN1122333A discloses a housing. See the search log.\n\n# Brief summary\n\nA sensor.\n",
        encoding="utf-8",
    )
    assert mod.scan(path.read_text(encoding="utf-8"))["flag_count"] == 0
    assert mod.main([str(path)]) == 0


def test_added_matter_marks_new_sentences_and_numbers(tmp_path):
    mod = load("added_matter.py")
    disclosure = tmp_path / "disclosure.md"
    description = tmp_path / "description.md"
    disclosure.write_text("壳体容纳传感器。The housing encloses the sensor.\n", encoding="utf-8")
    description.write_text(
        "\n".join(
            [
                "# 技术领域",
                "壳体容纳传感器。",
                "量子纠缠使产率达到37.5。",
                "The housing encloses the sensor during each cycle.",
                "Quantum yield tripled after annealing the wafer overnight.",
            ]
        ),
        encoding="utf-8",
    )
    report = mod.scan(description.read_text(encoding="utf-8"), disclosure.read_text(encoding="utf-8"))
    texts = [flag["text"] for flag in report["flags"]]
    assert any("量子纠缠" in text for text in texts)
    assert any("37.5" in flag["numbers"] for flag in report["flags"])
    assert any(text.startswith("Quantum yield") for text in texts)
    assert not any(text.startswith("壳体容纳") for text in texts)
    assert mod.main([str(description), str(disclosure)]) == 1


def test_added_matter_passes_when_sentences_are_in_the_disclosure(tmp_path):
    mod = load("added_matter.py")
    disclosure = tmp_path / "disclosure.md"
    description = tmp_path / "description.md"
    disclosure.write_text("壳体容纳传感器。The housing encloses the sensor.\n", encoding="utf-8")
    description.write_text("# 具体实施方式\n\n壳体容纳传感器。\n\nThe housing encloses the sensor.\n", encoding="utf-8")
    assert mod.scan(description.read_text(encoding="utf-8"), disclosure.read_text(encoding="utf-8"))["flag_count"] == 0
