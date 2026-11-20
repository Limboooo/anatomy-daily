#!/usr/bin/env python3
"""Split left humerus, radius, and ulna out of models/skeleton.glb.

These BodyParts3D 4.3 meshes are already in the full skeleton. The script
copies one mesh, moves its bounding-box center to the origin, and writes a
single-bone GLB for the lesson viewer. Positions are only translated.
Normals, indices, and the ivory material are copied. Nothing is smoothed,
decimated, or remodelled.

It also fills the lesson URL on the matching left and right bones inside
models/skeleton.glb and models/skeleton-sources.json, so tapping them on
skeleton.html opens the lesson. Clavicle and scapula already work that way.
"""

from __future__ import annotations

import json
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKELETON = ROOT / "models" / "skeleton.glb"
SOURCES = ROOT / "models" / "skeleton-sources.json"

BONES = {
    "left-humerus": {
        "out": ROOT / "models" / "humerus-left.glb",
        "lesson": "lessons/04-humerus.html",
        "also": ("right-humerus",),
    },
    "left-radius": {
        "out": ROOT / "models" / "radius-left.glb",
        "lesson": "lessons/07-radius.html",
        "also": ("right-radius",),
    },
    "left-ulna": {
        "out": ROOT / "models" / "ulna-left.glb",
        "lesson": "lessons/08-ulna.html",
        "also": ("right-ulna",),
    },
}


def read_glb(path: Path) -> tuple[dict, bytes]:
    data = path.read_bytes()
    if data[:4] != b"glTF":
        raise SystemExit(f"{path} is not a GLB")
    json_len, json_type = struct.unpack_from("<I4s", data, 12)
    if json_type != b"JSON":
        raise SystemExit(f"{path} JSON chunk missing")
    doc = json.loads(data[20 : 20 + json_len])
    bin_off = 20 + json_len
    bin_len, bin_type = struct.unpack_from("<I4s", data, bin_off)
    if bin_type != b"BIN\x00":
        raise SystemExit(f"{path} BIN chunk missing")
    blob = data[bin_off + 8 : bin_off + 8 + bin_len]
    return doc, blob


def view_bytes(doc: dict, blob: bytes, accessor_index: int) -> bytes:
    acc = doc["accessors"][accessor_index]
    view = doc["bufferViews"][acc["bufferView"]]
    start = view.get("byteOffset", 0)
    return blob[start : start + view["byteLength"]]


def center_positions(raw: bytes) -> tuple[bytes, list[float], list[float]]:
    count = len(raw) // 12
    vals = list(struct.unpack("<" + "f" * (count * 3), raw))
    xs, ys, zs = vals[0::3], vals[1::3], vals[2::3]
    center = (
        (min(xs) + max(xs)) / 2.0,
        (min(ys) + max(ys)) / 2.0,
        (min(zs) + max(zs)) / 2.0,
    )
    moved = []
    for i in range(count):
        moved.extend(
            (
                xs[i] - center[0],
                ys[i] - center[1],
                zs[i] - center[2],
            )
        )
    out_min = [min(moved[0::3]), min(moved[1::3]), min(moved[2::3])]
    out_max = [max(moved[0::3]), max(moved[1::3]), max(moved[2::3])]
    return struct.pack("<" + "f" * len(moved), *moved), out_min, out_max


def pad(data: bytes, fill: bytes) -> bytes:
    extra = (-len(data)) % 4
    return data + fill * extra


def write_glb(path: Path, doc: dict, blob: bytes) -> None:
    json_bytes = pad(json.dumps(doc, ensure_ascii=False, separators=(",", ":")).encode("utf-8"), b" ")
    bin_bytes = pad(blob, b"\x00")
    total = 12 + 8 + len(json_bytes) + 8 + len(bin_bytes)
    out = bytearray()
    out += b"glTF"
    out += struct.pack("<II", 2, total)
    out += struct.pack("<I4s", len(json_bytes), b"JSON")
    out += json_bytes
    out += struct.pack("<I4s", len(bin_bytes), b"BIN\x00")
    out += bin_bytes
    path.write_bytes(out)


def extract_one(doc: dict, blob: bytes, name: str, lesson: str, dest: Path) -> None:
    node = next(item for item in doc["nodes"] if item["name"] == name)
    mesh = doc["meshes"][node["mesh"]]
    prim = mesh["primitives"][0]
    positions, pos_min, pos_max = center_positions(view_bytes(doc, blob, prim["attributes"]["POSITION"]))
    normals = view_bytes(doc, blob, prim["attributes"]["NORMAL"])
    indices = view_bytes(doc, blob, prim["indices"])
    pos_count = len(positions) // 12
    nrm_count = len(normals) // 12
    idx_count = len(indices) // 2
    if nrm_count != pos_count:
        raise SystemExit(f"{name} normal count {nrm_count} != positions {pos_count}")
    blob_out = positions + normals + indices
    nrm_off = len(positions)
    idx_off = nrm_off + len(normals)
    extras = dict(node.get("extras") or {})
    extras["lesson"] = lesson
    single = {
        "asset": {"version": "2.0", "generator": "anatomy-daily tools/extract_limb_glbs.py"},
        "scene": 0,
        "scenes": [{"nodes": [0]}],
        "nodes": [{"name": name, "mesh": 0, "extras": extras}],
        "meshes": [
            {
                "name": name,
                "primitives": [
                    {
                        "attributes": {"POSITION": 0, "NORMAL": 1},
                        "indices": 2,
                        "material": 0,
                    }
                ],
            }
        ],
        "materials": doc["materials"],
        "accessors": [
            {
                "bufferView": 0,
                "componentType": 5126,
                "count": pos_count,
                "type": "VEC3",
                "min": pos_min,
                "max": pos_max,
            },
            {"bufferView": 1, "componentType": 5126, "count": nrm_count, "type": "VEC3"},
            {"bufferView": 2, "componentType": 5123, "count": idx_count, "type": "SCALAR"},
        ],
        "bufferViews": [
            {"buffer": 0, "byteOffset": 0, "byteLength": len(positions), "target": 34962},
            {"buffer": 0, "byteOffset": nrm_off, "byteLength": len(normals), "target": 34962},
            {"buffer": 0, "byteOffset": idx_off, "byteLength": len(indices), "target": 34963},
        ],
        "buffers": [{"byteLength": len(blob_out)}],
    }
    write_glb(dest, single, blob_out)
    print(
        f"{name}: verts {pos_count} indices {idx_count} "
        f"extents {[round(pos_max[i] - pos_min[i], 4) for i in range(3)]} "
        f"-> {dest.relative_to(ROOT)} {dest.stat().st_size} bytes"
    )


def set_lesson_in_json(raw: bytearray, name: str, lesson: str) -> None:
    key = f'"name":"{name}"'.encode()
    start = raw.find(key)
    if start < 0:
        raise SystemExit(f"skeleton node {name} not found")
    nxt = raw.find(b'"name":', start + len(key))
    window = raw[start:nxt if nxt > 0 else None]
    empty = b'"lesson":""'
    if window.count(empty) != 1:
        raise SystemExit(f"{name} has {window.count(empty)} empty lesson fields")
    filled = f'"lesson":"{lesson}"'.encode()
    raw[start:nxt if nxt > 0 else len(raw)] = window.replace(empty, filled, 1)


def patch_skeleton(lesson_by_node: dict[str, str]) -> None:
    data = bytearray(SKELETON.read_bytes())
    json_len, json_type = struct.unpack_from("<I4s", data, 12)
    if json_type != b"JSON":
        raise SystemExit("skeleton JSON chunk missing")
    bin_at = 20 + json_len
    bin_len, bin_type = struct.unpack_from("<I4s", data, bin_at)
    if bin_type != b"BIN\x00":
        raise SystemExit("skeleton BIN chunk missing")
    binary = bytes(data[bin_at : bin_at + 8 + bin_len])
    raw = bytearray(bytes(data[20 : 20 + json_len]).rstrip(b" "))
    for name, lesson in lesson_by_node.items():
        set_lesson_in_json(raw, name, lesson)
    json.loads(raw)  # refuse to write a broken document
    padded = pad(bytes(raw), b" ")
    total = 12 + 8 + len(padded) + len(binary)
    out = bytearray()
    out += b"glTF"
    out += struct.pack("<II", 2, total)
    out += struct.pack("<I4s", len(padded), b"JSON")
    out += padded
    out += binary
    SKELETON.write_bytes(out)
    print(f"skeleton.glb lesson links updated, {len(out)} bytes")


def patch_sources(lesson_by_id: dict[str, str]) -> None:
    text = SOURCES.read_text(encoding="utf-8")
    for bone_id, lesson in lesson_by_id.items():
        marker = f'"id": "{bone_id}"'
        start = text.find(marker)
        if start < 0:
            raise SystemExit(f"sources id {bone_id} not found")
        nxt = text.find('"id":', start + len(marker))
        window = text[start:nxt if nxt > 0 else None]
        old = '"lesson": ""'
        if window.count(old) != 1:
            raise SystemExit(f"{bone_id} lesson count {window.count(old)}")
        window = window.replace(old, f'"lesson": "{lesson}"', 1)
        text = text[:start] + window + text[nxt if nxt > 0 else len(text) :]
    SOURCES.write_text(text, encoding="utf-8")
    print("skeleton-sources.json lesson links updated")


def main() -> None:
    doc, blob = read_glb(SKELETON)
    lesson_by_node: dict[str, str] = {}
    for name, spec in BONES.items():
        extract_one(doc, blob, name, spec["lesson"], spec["out"])
        lesson_by_node[name] = spec["lesson"]
        for other in spec["also"]:
            lesson_by_node[other] = spec["lesson"]
    patch_skeleton(lesson_by_node)
    patch_sources(lesson_by_node)


if __name__ == "__main__":
    main()
