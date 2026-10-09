"""Visual sheet checks. Fixture PNGs are generated in the test."""

import importlib.util
import json
import struct
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "check_sheets.py"


def load_module():
    spec = importlib.util.spec_from_file_location("check_sheets_mod", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def png_bytes(width, height, paint):
    def chunk(tag, data):
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    raw = bytearray()
    for y in range(height):
        raw.append(0)
        for x in range(width):
            red, green, blue = paint(x, y)
            raw.extend((red, green, blue))
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) + chunk(b"IDAT", zlib.compress(bytes(raw))) + chunk(b"IEND", b"")


def black_line(x, y):
    return (0, 0, 0) if y == 0 else (255, 255, 255)


def prepare(tmp_path, paint=black_line):
    mod = load_module()
    drawings = tmp_path / "07-drawings"
    drawings.mkdir(parents=True)
    image = png_bytes(6, 6, paint)
    (drawings / "fig1.png").write_bytes(image)
    digest = mod.sha256_file(drawings / "fig1.png")
    master = {
        "frozen": True,
        "parts": [{"id": "10", "name": "housing", "kind": "part"}],
        "relationships": [
            {"id": "R1", "claim": "1", "text": "housing encloses the sensor", "visible_on": ["FIG. 1"]}
        ],
    }
    manifest = {
        "sheets": [
            {
                "id": "FIG. 1",
                "image": "fig1.png",
                "source": "fig1.dot",
                "source_kind": "graphviz",
                "sha256": digest,
            }
        ]
    }
    (drawings / "parts_master.json").write_text(json.dumps(master), encoding="utf-8")
    (drawings / "sheet_manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    look = {
        "sheets": [
            {
                "id": "FIG. 1",
                "numerals_match_master": True,
                "black_on_white_seen": True,
                "relationships_seen": ["R1"],
            }
        ]
    }
    look_path = drawings / "visual_look.json"
    look_path.write_text(json.dumps(look), encoding="utf-8")
    return mod, drawings, look_path


def test_opens_black_on_white_sheet(tmp_path):
    mod, drawings, look_path = prepare(tmp_path)
    code = mod.main(["--drawings", str(drawings), "--look", str(look_path), "--format", "json"])
    assert code == 0
    report = mod.analyze(drawings, json.loads(look_path.read_text(encoding="utf-8")))
    assert report["sheets"][0]["opened"] is True
    assert report["sheets"][0]["black_on_white"] is True
    assert report["sheets"][0]["width"] == 6


def test_colored_sheet_fails_even_if_look_says_pass(tmp_path):
    def red(x, y):
        return (200, 0, 0) if (x, y) == (0, 0) else (255, 255, 255)

    mod, drawings, look_path = prepare(tmp_path, red)
    # prepare hashed the colored png, so the checksum matches; pixels must still fail
    code = mod.main(["--drawings", str(drawings), "--look", str(look_path), "--format", "json"])
    assert code == 1
    report = mod.analyze(drawings, json.loads(look_path.read_text(encoding="utf-8")))
    codes = {item["code"] for item in report["errors"]}
    assert "not_black_on_white" in codes
    assert "look_disagrees_with_pixels" in codes
    assert "set_restart" in codes


def test_shading_and_blank_fail(tmp_path):
    mod, drawings, look_path = prepare(tmp_path, lambda x, y: (140, 140, 140))
    report = mod.analyze(drawings, json.loads(look_path.read_text(encoding="utf-8")))
    assert any(item["code"] == "not_black_on_white" for item in report["errors"])

    mod, drawings, look_path = prepare(tmp_path / "blank", lambda x, y: (255, 255, 255))
    report = mod.analyze(drawings, json.loads(look_path.read_text(encoding="utf-8")))
    assert any(item["code"] == "blank_sheet" for item in report["errors"])


def test_checksum_change_restarts_set(tmp_path):
    mod, drawings, look_path = prepare(tmp_path)
    (drawings / "fig1.png").write_bytes(png_bytes(6, 6, lambda x, y: (0, 0, 0)))
    code = mod.main(["--drawings", str(drawings), "--look", str(look_path), "--format", "json"])
    assert code == 1
    report = mod.analyze(drawings, json.loads(look_path.read_text(encoding="utf-8")))
    assert any(item["code"] == "checksum_mismatch" for item in report["errors"])
    assert any(item["code"] == "set_restart" for item in report["errors"])


def test_relationship_must_name_a_figure(tmp_path):
    mod, drawings, look_path = prepare(tmp_path)
    master = json.loads((drawings / "parts_master.json").read_text(encoding="utf-8"))
    master["relationships"][0]["visible_on"] = []
    (drawings / "parts_master.json").write_text(json.dumps(master), encoding="utf-8")
    report = mod.analyze(drawings, json.loads(look_path.read_text(encoding="utf-8")))
    assert any(item["code"] == "relationship_without_figure" for item in report["errors"])


def test_missing_look_is_a_failure(tmp_path):
    mod, drawings, _look_path = prepare(tmp_path)
    code = mod.main(["--drawings", str(drawings), "--format", "json"])
    assert code == 1
    report = mod.analyze(drawings, None)
    assert report["sheets"][0]["opened"] is True
    assert any(item["code"] == "visual_look_missing" for item in report["errors"])
