"""Checksum tests. PNGs are generated here and are not stored in the repo."""

import importlib.util
import json
import struct
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "sheet_checksums.py"


def load_module():
    spec = importlib.util.spec_from_file_location("sheet_checksums_mod", SCRIPT)
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


def write_master(drawings: Path, frozen: bool = True) -> None:
    payload = {
        "frozen": frozen,
        "parts": [{"id": "10", "name": "housing", "kind": "part"}],
        "relationships": [
            {"id": "R1", "claim": "1", "text": "housing holds the sensor", "visible_on": ["FIG. 1"]}
        ],
    }
    (drawings / "parts_master.json").write_text(json.dumps(payload), encoding="utf-8")


def write_sheet(drawings: Path) -> None:
    drawings.mkdir(parents=True, exist_ok=True)
    (drawings / "fig1.png").write_bytes(png_bytes(4, 4, black_line))
    (drawings / "fig1.dot").write_text("digraph G { housing -> sensor }\n", encoding="utf-8")


def test_build_hashes_png_from_graphviz(tmp_path):
    mod = load_module()
    drawings = tmp_path / "07-drawings"
    write_sheet(drawings)
    write_master(drawings)
    plan = {
        "sheets": [
            {"id": "FIG. 1", "image": "fig1.png", "source": "fig1.dot", "source_kind": "graphviz"}
        ]
    }
    plan_path = tmp_path / "plan.json"
    plan_path.write_text(json.dumps(plan), encoding="utf-8")
    out = drawings / "sheet_manifest.json"
    code = mod.main(["build", "--drawings", str(drawings), "--plan", str(plan_path), "--out", str(out)])
    assert code == 0
    manifest = json.loads(out.read_text(encoding="utf-8"))
    assert manifest["sheets"][0]["sha256"] == mod.sha256_file(drawings / "fig1.png")
    assert manifest["sheets"][0]["source_kind"] == "graphviz"
    assert mod.main(["verify", "--drawings", str(drawings), "--manifest", str(out)]) == 0


def test_rejects_image_model_and_unfrozen_master(tmp_path):
    mod = load_module()
    drawings = tmp_path / "07-drawings"
    write_sheet(drawings)
    write_master(drawings, frozen=False)
    plan_path = tmp_path / "plan.json"
    plan_path.write_text(
        json.dumps(
            {
                "sheets": [
                    {
                        "id": "FIG. 1",
                        "image": "fig1.png",
                        "source": "fig1.dot",
                        "source_kind": "image_model",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    out = drawings / "sheet_manifest.json"
    assert mod.main(["build", "--drawings", str(drawings), "--plan", str(plan_path), "--out", str(out)]) == 1
    assert not out.exists()

    write_master(drawings, frozen=True)
    assert mod.main(["build", "--drawings", str(drawings), "--plan", str(plan_path), "--out", str(out)]) == 1
    assert not out.exists()


def test_rejects_invented_spectrum_and_accepts_inventor_data(tmp_path):
    mod = load_module()
    drawings = tmp_path / "07-drawings"
    write_sheet(drawings)
    write_master(drawings)
    (drawings / "plot.py").write_text("print('plot')\n", encoding="utf-8")
    plan_path = tmp_path / "plan.json"
    out = drawings / "sheet_manifest.json"
    plan_path.write_text(
        json.dumps(
            {
                "sheets": [
                    {
                        "id": "FIG. 1",
                        "image": "fig1.png",
                        "source": "plot.py",
                        "source_kind": "matplotlib",
                        "content": "spectrum",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    assert mod.main(["build", "--drawings", str(drawings), "--plan", str(plan_path), "--out", str(out)]) == 1

    (drawings / "absorbance.csv").write_text("nm,abs\n400,0.1\n", encoding="utf-8")
    plan_path.write_text(
        json.dumps(
            {
                "sheets": [
                    {
                        "id": "FIG. 1",
                        "image": "fig1.png",
                        "source": "plot.py",
                        "source_kind": "matplotlib",
                        "content": "spectrum",
                        "data_file": "absorbance.csv",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    assert mod.main(["build", "--drawings", str(drawings), "--plan", str(plan_path), "--out", str(out)]) == 0


def test_verify_fails_when_png_changes(tmp_path):
    mod = load_module()
    drawings = tmp_path / "07-drawings"
    write_sheet(drawings)
    write_master(drawings)
    plan_path = tmp_path / "plan.json"
    plan_path.write_text(
        json.dumps(
            {"sheets": [{"id": "FIG. 1", "image": "fig1.png", "source": "fig1.dot", "source_kind": "graphviz"}]}
        ),
        encoding="utf-8",
    )
    out = drawings / "sheet_manifest.json"
    assert mod.main(["build", "--drawings", str(drawings), "--plan", str(plan_path), "--out", str(out)]) == 0
    (drawings / "fig1.png").write_bytes(png_bytes(4, 4, lambda x, y: (255, 255, 255)))
    assert mod.main(["verify", "--drawings", str(drawings), "--manifest", str(out)]) == 1


def test_rejects_traced_art_and_invented_structure(tmp_path):
    mod = load_module()
    drawings = tmp_path / "07-drawings"
    write_sheet(drawings)
    write_master(drawings)
    (drawings / "mol.drawio").write_text("<mxfile/>", encoding="utf-8")
    plan_path = tmp_path / "plan.json"
    out = drawings / "sheet_manifest.json"
    plan_path.write_text(
        json.dumps(
            {
                "sheets": [
                    {
                        "id": "FIG. 1",
                        "image": "fig1.png",
                        "source": "mol.drawio",
                        "source_kind": "traced_art",
                        "content": "chemical_structure",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    assert mod.main(["build", "--drawings", str(drawings), "--plan", str(plan_path), "--out", str(out)]) == 1
    plan_path.write_text(
        json.dumps(
            {
                "sheets": [
                    {
                        "id": "FIG. 1",
                        "image": "fig1.png",
                        "source": "mol.drawio",
                        "source_kind": "drawio",
                        "content": "chemical_structure",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    assert mod.main(["build", "--drawings", str(drawings), "--plan", str(plan_path), "--out", str(out)]) == 1
    (drawings / "inventor.mol").write_text("inventor structure\n", encoding="utf-8")
    plan_path.write_text(
        json.dumps(
            {
                "sheets": [
                    {
                        "id": "FIG. 1",
                        "image": "fig1.png",
                        "source": "mol.drawio",
                        "source_kind": "drawio",
                        "content": "chemical_structure",
                        "structure_source": "inventor.mol",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    assert mod.main(["build", "--drawings", str(drawings), "--plan", str(plan_path), "--out", str(out)]) == 0
