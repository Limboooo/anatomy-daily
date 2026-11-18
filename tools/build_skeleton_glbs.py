#!/usr/bin/env python3
"""Build the full-skeleton and shoulder-girdle GLBs from BodyParts3D 4.3 OBJs.

The site does not run this script. It records the only changes made to the
meshes: one shared rigid axis change into glTF Y-up, millimetres to metres,
one translation that centers the whole assembly, and recomputed vertex
normals. Vertices are not smoothed, decimated, or remodelled.

When a concept has two overlapping FJ files, the higher FJ number is kept.
That is the same choice the clavicle lesson already documents (FJ6347, not
the older FJ3237). A file whose centroid sits on the wrong side of the
midline is dropped: a few newer right-hand phalanx files in this release are
placed on the left. Left hip bone FJ3288 is dropped because it duplicates
Bony part of left hip bone FJ6398.

Expected input is the flat directory of 4.3 element OBJs named
FJ*_BP*_FMA*_English name.obj, with the Anatomography header intact.

Usage:
  python3 tools/build_skeleton_glbs.py /path/to/objs
"""

from __future__ import annotations

import hashlib
import json
import re
import struct
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SKELETON_OUT = ROOT / "models" / "skeleton.glb"
SHOULDER_OUT = ROOT / "models" / "shoulder-left.glb"
SOURCES_OUT = ROOT / "models" / "skeleton-sources.json"

CLAVICLE_SHA = "7bd988c1e54e9696d581e4be2e94f5de9cc08c00260dcf88aba42cc21f0b533f"
SCAPULA_SHA = "87cebf8702718e03dd10afbee87a50abce47139802ff305c749b33f40d451fda"
SHOULDER_FJ = {"clavicle": "FJ6347", "scapula": "FJ3279", "humerus": "FJ6373"}

BONE_COLOR = (0.90, 0.84, 0.73, 1.0)
COPYRIGHT = (
    "BodyParts3D, © The Database Center for Life Science "
    "licensed under CC Attribution 4.0 International"
)

ORD = {
    "first": "第一",
    "second": "第二",
    "third": "第三",
    "fourth": "第四",
    "fifth": "第五",
    "sixth": "第六",
    "seventh": "第七",
    "eighth": "第八",
    "ninth": "第九",
    "tenth": "第十",
    "eleventh": "第十一",
    "twelfth": "第十二",
}
ORD_RE = "|".join(ORD)
SIMPLE = {
    "clavicle": "锁骨",
    "scapula": "肩胛骨",
    "humerus": "肱骨",
    "radius": "桡骨",
    "ulna": "尺骨",
    "femur": "股骨",
    "patella": "髌骨",
    "tibia": "胫骨",
    "fibula": "腓骨",
    "hip bone": "髋骨",
    "calcaneus": "跟骨",
    "talus": "距骨",
    "cuboid bone": "骰骨",
    "medial cuneiform bone": "内侧楔骨",
    "intermediate cuneiform bone": "中间楔骨",
    "lateral cuneiform bone": "外侧楔骨",
    "scaphoid": "手舟骨",
    "lunate": "月骨",
    "triquetral": "三角骨",
    "pisiform": "豌豆骨",
    "trapezium": "大多角骨",
    "trapezoid": "小多角骨",
    "capitate": "头状骨",
    "hamate": "钩骨",
    "inferior nasal concha": "下鼻甲",
    "nasal bone": "鼻骨",
    "lacrimal bone": "泪骨",
    "zygomatic bone": "颧骨",
    "parietal bone": "顶骨",
    "temporal bone": "颞骨",
    "palatine bone": "腭骨",
    "maxilla": "上颌骨",
}
UNSIDED = {
    "frontal bone": "额骨",
    "occipital bone": "枕骨",
    "sphenoid bone": "蝶骨",
    "ethmoid": "筛骨",
    "perpendicular plate of ethmoid": "筛骨垂直板",
    "vomer": "犁骨",
    "mandible": "下颌骨",
    "hyoid bone": "舌骨",
    "manubrium": "胸骨柄",
    "body of sternum": "胸骨体",
    "xiphoid process": "剑突",
    "sacrum": "骶骨",
    "atlas": "寰椎",
    "axis": "枢椎",
}
DIGIT = {
    "thumb": ("拇指", "指骨"),
    "index finger": ("食指", "指骨"),
    "middle finger": ("中指", "指骨"),
    "ring finger": ("无名指", "指骨"),
    "little finger": ("小指", "指骨"),
    "big toe": ("大脚趾", "趾骨"),
    "second toe": ("第二趾", "趾骨"),
    "third toe": ("第三趾", "趾骨"),
    "fourth toe": ("第四趾", "趾骨"),
    "little toe": ("小趾", "趾骨"),
}
LEVEL = {"distal": "远节", "middle": "中节", "proximal": "近节"}
TOOTH = {
    "central incisor": "中切牙",
    "lateral incisor": "侧切牙",
    "canine": "尖牙",
    "premolar": "前磨牙",
    "molar": "磨牙",
}
REGION = {
    "cervical": "颈椎",
    "thoracic": "胸椎",
    "lumbar": "腰椎",
}


def parse_obj(path: Path):
    verts = []
    faces = []
    header = {"name": "", "fj": "", "bp": "", "fma": "", "version": ""}
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if line.startswith("# English name"):
            header["name"] = line.split(":", 1)[1].strip()
        elif line.startswith("# File ID"):
            header["fj"] = line.split(":", 1)[1].strip()
        elif line.startswith("# Representation ID"):
            header["bp"] = line.split(":", 1)[1].strip()
        elif line.startswith("# Concept ID"):
            header["fma"] = line.split(":", 1)[1].strip()
        elif line.startswith("# Compatibility version"):
            header["version"] = line.split(":", 1)[1].strip()
        elif line.startswith("v "):
            x, y, z = line.split()[1:4]
            verts.append((float(x), float(y), float(z)))
        elif line.startswith("f "):
            idx = [int(tok.split("/", 1)[0]) - 1 for tok in line.split()[1:]]
            if len(idx) == 3:
                faces.append(idx)
            elif len(idx) > 3:
                for i in range(1, len(idx) - 1):
                    faces.append((idx[0], idx[i], idx[i + 1]))
    if not verts or not faces:
        raise SystemExit(f"{path} has no mesh")
    return np.asarray(verts, np.float64), np.asarray(faces, np.int32), header


def wanted(name: str) -> bool:
    n = name.lower()
    if n in UNSIDED:
        return True
    if re.search(r"\bscapula\b", n) and "subscapular" not in n:
        return True
    keys = (
        "clavicle",
        "humerus",
        "radius",
        "ulna",
        "femur",
        "patella",
        "tibia",
        "fibula",
        "hip bone",
        "calcaneus",
        "talus",
        "cuboid bone",
        "cuneiform bone",
        "metacarpal bone",
        "metatarsal bone",
        "scaphoid",
        "lunate",
        "triquetral",
        "pisiform",
        "trapezium",
        "trapezoid",
        "capitate",
        "hamate",
        "inferior nasal concha",
        "nasal bone",
        "lacrimal bone",
        "zygomatic bone",
        "parietal bone",
        "temporal bone",
        "palatine bone",
        "maxilla",
        "phalanx of ",
        " costal cartilage",
        " rib",
        " vertebra",
        "sesamoid bone of ",
        " tooth",
        "navicular bone of ",
    )
    return any(k in n for k in keys)


def side_of(name: str) -> str | None:
    n = name.lower()
    if n.startswith("left ") or " of left " in n:
        return "left"
    if n.startswith("right ") or " of right " in n:
        return "right"
    return None


def fj_number(fj: str) -> int:
    match = re.match(r"FJ(\d+)", fj)
    if not match:
        raise SystemExit(f"bad FJ id {fj}")
    return int(match.group(1))


def box_iou(a_min, a_max, b_min, b_max) -> float:
    lo = np.maximum(a_min, b_min)
    hi = np.minimum(a_max, b_max)
    inter = float(np.prod(np.maximum(hi - lo, 0.0)))
    if inter <= 0:
        return 0.0
    va = float(np.prod(a_max - a_min))
    vb = float(np.prod(b_max - b_min))
    return inter / (va + vb - inter)


def zh_name(name: str, medial: bool | None = None) -> str:
    raw = name.strip()
    low = raw.lower()
    if low in UNSIDED:
        return UNSIDED[low]
    if low == "bony part of left hip bone":
        return "左髋骨"

    phalanx = re.match(
        r"(Distal|Middle|Proximal) phalanx of (left|right) (.+)$", raw, re.I
    )
    if phalanx:
        level, side, digit = phalanx.groups()
        label, kind = DIGIT[digit.lower()]
        return f"{'左' if side.lower()=='left' else '右'}{label}{LEVEL[level.lower()]}{kind}"

    tooth = re.match(
        r"(Left|Right) (first |second )?(upper|lower) "
        r"(central incisor|lateral incisor|canine|premolar|molar) tooth$",
        raw,
        re.I,
    )
    if tooth:
        side, nth, jaw, kind = tooth.groups()
        num = ORD[nth.strip()] if nth else ""
        return (
            f"{'左' if side.lower()=='left' else '右'}"
            f"{'上' if jaw.lower()=='upper' else '下'}{num}{TOOTH[kind.lower()]}"
        )

    rib = re.match(rf"(Left|Right) ({ORD_RE}) rib$", raw, re.I)
    if rib:
        side, nth = rib.groups()
        return f"{'左' if side.lower()=='left' else '右'}{ORD[nth.lower()]}肋"

    cartilage = re.match(rf"(Left|Right) ({ORD_RE}) costal cartilage$", raw, re.I)
    if cartilage:
        side, nth = cartilage.groups()
        return f"{'左' if side.lower()=='left' else '右'}{ORD[nth.lower()]}肋软骨"

    vertebra = re.match(rf"({ORD_RE}) (cervical|thoracic|lumbar) vertebra$", raw, re.I)
    if vertebra:
        nth, region = vertebra.groups()
        return f"{ORD[nth.lower()]}{REGION[region.lower()]}"

    meta = re.match(
        rf"(Left|Right) ({ORD_RE}) (metacarpal|metatarsal) bone$", raw, re.I
    )
    if meta:
        side, nth, kind = meta.groups()
        bone = "掌骨" if kind.lower() == "metacarpal" else "跖骨"
        return f"{'左' if side.lower()=='left' else '右'}{ORD[nth.lower()]}{bone}"

    nav = re.match(r"Navicular bone of (left|right) foot$", raw, re.I)
    if nav:
        return f"{'左' if nav.group(1).lower()=='left' else '右'}足舟骨"

    ses = re.match(r"Sesamoid bone of (left|right) foot$", raw, re.I)
    if ses:
        where = "内侧" if medial else "外侧"
        return f"{'左' if ses.group(1).lower()=='left' else '右'}足{where}籽骨"

    side = side_of(raw)
    prefix = {"left": "左", "right": "右"}.get(side or "", "")
    rest = raw
    if side == "left":
        rest = raw[5:]
    elif side == "right":
        rest = raw[6:]
    label = SIMPLE.get(rest.lower())
    if label:
        return prefix + label
    raise SystemExit(f"no Chinese name for {name}")


def slug(name: str, extra: str = "") -> str:
    if name.lower() == "bony part of left hip bone":
        base = "left-hip-bone"
    else:
        base = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return f"{base}-{extra}" if extra else base


def lesson_for(name: str) -> str:
    low = name.lower()
    if "clavicle" in low:
        return "lessons/01-clavicle.html"
    if re.search(r"\bscapula\b", low):
        return "lessons/02-scapula.html"
    return ""


def to_gltf(vertices: np.ndarray) -> np.ndarray:
    """BodyParts3D millimetres, +X left, +Y posterior, +Z superior.

    glTF is metres, +Y up, +Z anterior (toward the default camera).
    """
    x, y, z = vertices[:, 0], vertices[:, 1], vertices[:, 2]
    return np.stack([x, z, -y], axis=1) * 0.001


def orient_faces(vertices: np.ndarray, faces: np.ndarray) -> np.ndarray:
    a = vertices[faces[:, 0]]
    b = vertices[faces[:, 1]]
    c = vertices[faces[:, 2]]
    normals = np.cross(b - a, c - a)
    centers = (a + b + c) / 3.0
    if float(np.sum(normals * (centers - vertices.mean(axis=0)))) < 0:
        return faces[:, ::-1].copy()
    return faces


def vertex_normals(vertices: np.ndarray, faces: np.ndarray) -> np.ndarray:
    a = vertices[faces[:, 0]]
    b = vertices[faces[:, 1]]
    c = vertices[faces[:, 2]]
    face_n = np.cross(b - a, c - a)
    normals = np.zeros_like(vertices)
    for column in range(3):
        np.add.at(normals, faces[:, column], face_n)
    length = np.linalg.norm(normals, axis=1)
    length[length == 0] = 1.0
    return normals / length[:, None]


def unit(vector: np.ndarray) -> np.ndarray:
    vector = np.asarray(vector, np.float64)
    return vector / np.linalg.norm(vector)


def rodrigues(point: np.ndarray, origin: np.ndarray, axis: np.ndarray, degrees: float) -> np.ndarray:
    theta = np.deg2rad(degrees)
    axis = unit(axis)
    cos, sin = np.cos(theta), np.sin(theta)
    offset = point - origin
    rotated = (
        offset * cos
        + np.cross(axis, offset) * sin
        + axis * np.dot(axis, offset) * (1.0 - cos)
    )
    return origin + rotated


def pca_small(vertices: np.ndarray) -> np.ndarray:
    centered = vertices - vertices.mean(axis=0)
    _, eigvec = np.linalg.eigh(np.cov(centered.T))
    return unit(eigvec[:, 0])


def endpoints(vertices: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    centered = vertices - vertices.mean(axis=0)
    _, eigvec = np.linalg.eigh(np.cov(centered.T))
    axis = unit(eigvec[:, -1])
    proj = centered @ axis
    return vertices[int(np.argmin(proj))].copy(), vertices[int(np.argmax(proj))].copy()


def closest_vertex(vertices: np.ndarray, point: np.ndarray) -> np.ndarray:
    index = int(np.argmin(np.linalg.norm(vertices - point, axis=1)))
    return vertices[index].copy()


def sphere_center(points: np.ndarray) -> np.ndarray:
    """Least-squares sphere center. The humeral head is the ball."""
    xx = np.sum(points * points, axis=1)
    design = np.column_stack([points, np.ones(len(points))])
    coef, *_ = np.linalg.lstsq(design, xx, rcond=None)
    return coef[:3] / 2.0


def axis_that_increases(point, origin, candidate, score) -> np.ndarray:
    axis = unit(candidate)
    moved = rodrigues(point, origin, axis, 12.0)
    if score(moved) <= score(point):
        axis = -axis
        moved = rodrigues(point, origin, axis, 12.0)
        if score(moved) <= score(point):
            raise SystemExit("rotation axis does not move the landmark")
    return axis


def r6(values) -> list[float]:
    return [round(float(v), 6) for v in np.asarray(values).tolist()]


def select_parts(folder: Path) -> list[dict]:
    grouped: dict[str, list[dict]] = {}
    for path in sorted(folder.glob("*.obj")):
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        vertices, faces, header = parse_obj(path)
        if header["version"] != "4.3":
            continue
        if not wanted(header["name"]):
            continue
        if header["fj"] == "FJ6347" and digest != CLAVICLE_SHA:
            raise SystemExit("FJ6347 hash does not match the clavicle lesson")
        if header["fj"] == "FJ3279" and digest != SCAPULA_SHA:
            raise SystemExit("FJ3279 hash does not match the scapula lesson")
        side = side_of(header["name"])
        midline = float(vertices[:, 0].mean())
        if side == "left" and midline < -5:
            continue
        if side == "right" and midline > 5:
            continue
        item = {
            "path": path,
            "sha256": digest,
            "vertices": vertices,
            "faces": faces,
            "name": header["name"],
            "fj": header["fj"],
            "bp": header["bp"],
            "fma": header["fma"],
            "mn": vertices.min(axis=0),
            "mx": vertices.max(axis=0),
            "centroid": vertices.mean(axis=0),
        }
        grouped.setdefault(header["name"], []).append(item)

    chosen: list[dict] = []
    for name, items in grouped.items():
        items.sort(key=lambda item: fj_number(item["fj"]), reverse=True)
        kept: list[dict] = []
        for item in items:
            if any(box_iou(item["mn"], item["mx"], prev["mn"], prev["mx"]) > 0.25 for prev in kept):
                continue
            kept.append(item)
        if "sesamoid" in name.lower() and len(kept) == 2:
            kept.sort(key=lambda item: abs(float(item["centroid"][0])))
            for item, medial in zip(kept, (True, False)):
                item["medial"] = medial
        else:
            for item in kept:
                item["medial"] = None
        chosen.extend(kept)

    # Left hip bone FJ3288 is an older copy of Bony part of left hip bone.
    # Neighbouring ribs also have overlapping boxes, so this is name-specific.
    has_bony_hip = any(item["name"] == "Bony part of left hip bone" for item in chosen)
    unique = [
        item
        for item in chosen
        if not (has_bony_hip and item["name"] == "Left hip bone")
    ]
    unique.sort(key=lambda item: item["name"])

    seen = set()
    for item in unique:
        item["zh"] = zh_name(item["name"], item["medial"])
        extra = ""
        if item["medial"] is True:
            extra = "medial"
        elif item["medial"] is False:
            extra = "lateral"
        item["id"] = slug(item["name"], extra)
        if item["id"] in seen:
            raise SystemExit(f"duplicate id {item['id']}")
        seen.add(item["id"])
        item["lesson"] = lesson_for(item["name"])
    return unique


def expect_counts(parts: list[dict]) -> None:
    names = [part["name"] for part in parts]
    by_fj = {part["fj"]: part for part in parts}

    def count(pred) -> int:
        return sum(1 for name in names if pred(name.lower()))

    checks = {
        "clavicle": count(lambda n: "clavicle" in n),
        "scapula": count(lambda n: bool(re.search(r"\bscapula\b", n))),
        "humerus": count(lambda n: n.endswith("humerus") or " humerus" in n),
        "rib": count(lambda n: n.endswith(" rib")),
        "cartilage": count(lambda n: n.endswith("costal cartilage")),
        "cervical": count(lambda n: "cervical vertebra" in n) + count(lambda n: n in {"atlas", "axis"}),
        "thoracic": count(lambda n: "thoracic vertebra" in n),
        "lumbar": count(lambda n: "lumbar vertebra" in n),
        "phalanx": count(lambda n: "phalanx of " in n),
    }
    expected = {
        "clavicle": 2,
        "scapula": 2,
        "humerus": 2,
        "rib": 24,
        "cartilage": 20,
        "cervical": 7,
        "thoracic": 12,
        "lumbar": 5,
        "phalanx": 56,
    }
    for key, want in expected.items():
        if checks[key] != want:
            raise SystemExit(f"{key}: expected {want}, got {checks[key]}")
    for kind, fj in SHOULDER_FJ.items():
        if fj not in by_fj:
            raise SystemExit(f"shoulder {kind} {fj} was not selected")
    if not any(part["name"] == "Sacrum" for part in parts):
        raise SystemExit("sacrum missing")
    if not any(part["name"] == "Mandible" for part in parts):
        raise SystemExit("mandible missing")
    print("counts", checks, "parts", len(parts))


def prepare_mesh(part: dict, center: np.ndarray) -> dict:
    vertices = to_gltf(part["vertices"]) - center
    faces = orient_faces(vertices, part["faces"])
    normals = vertex_normals(vertices, faces)
    return {
        "id": part["id"],
        "vertices": np.asarray(vertices, np.float32),
        "faces": faces.astype(np.uint32),
        "normals": np.asarray(normals, np.float32),
        "extras": {
            "zh": part["zh"],
            "lesson": part["lesson"],
            "fj": part["fj"],
            "bp": part["bp"],
            "fma": part["fma"],
            "en": part["name"],
        },
    }


def write_glb(path: Path, meshes: list[dict], scene_extras: dict | None = None) -> None:
    blob = bytearray()
    buffer_views = []
    accessors = []

    def align() -> None:
        while len(blob) % 4:
            blob.append(0)

    def add_view(data: bytes, target: int) -> int:
        align()
        offset = len(blob)
        blob.extend(data)
        buffer_views.append(
            {"buffer": 0, "byteOffset": offset, "byteLength": len(data), "target": target}
        )
        return len(buffer_views) - 1

    nodes = []
    gl_meshes = []
    for mesh in meshes:
        position = np.ascontiguousarray(mesh["vertices"], np.float32)
        normal = np.ascontiguousarray(mesh["normals"], np.float32)
        index = mesh["faces"].reshape(-1)
        if int(position.shape[0]) < 65536:
            index = np.ascontiguousarray(index, np.uint16)
            index_type = 5123
        else:
            index = np.ascontiguousarray(index, np.uint32)
            index_type = 5125
        pos_view = add_view(position.tobytes(), 34962)
        nor_view = add_view(normal.tobytes(), 34962)
        idx_view = add_view(index.tobytes(), 34963)
        pos_acc = len(accessors)
        accessors.append(
            {
                "bufferView": pos_view,
                "componentType": 5126,
                "count": int(position.shape[0]),
                "type": "VEC3",
                "min": [float(v) for v in position.min(axis=0)],
                "max": [float(v) for v in position.max(axis=0)],
            }
        )
        nor_acc = len(accessors)
        accessors.append(
            {
                "bufferView": nor_view,
                "componentType": 5126,
                "count": int(normal.shape[0]),
                "type": "VEC3",
            }
        )
        idx_acc = len(accessors)
        accessors.append(
            {
                "bufferView": idx_view,
                "componentType": index_type,
                "count": int(index.size),
                "type": "SCALAR",
            }
        )
        gl_meshes.append(
            {
                "name": mesh["id"],
                "primitives": [
                    {
                        "attributes": {"POSITION": pos_acc, "NORMAL": nor_acc},
                        "indices": idx_acc,
                        "material": 0,
                    }
                ],
            }
        )
        nodes.append({"name": mesh["id"], "mesh": len(gl_meshes) - 1, "extras": mesh["extras"]})

    gltf = {
        "asset": {
            "version": "2.0",
            "generator": "anatomy-daily tools/build_skeleton_glbs.py",
            "copyright": COPYRIGHT,
        },
        "scene": 0,
        "scenes": [{"nodes": list(range(len(nodes))), "extras": scene_extras or {}}],
        "nodes": nodes,
        "meshes": gl_meshes,
        "materials": [
            {
                "name": "bone",
                "doubleSided": True,
                "pbrMetallicRoughness": {
                    "baseColorFactor": list(BONE_COLOR),
                    "metallicFactor": 0.0,
                    "roughnessFactor": 0.62,
                },
            }
        ],
        "buffers": [{"byteLength": len(blob)}],
        "bufferViews": buffer_views,
        "accessors": accessors,
    }
    json_bytes = json.dumps(gltf, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    while len(json_bytes) % 4:
        json_bytes += b" "
    while len(blob) % 4:
        blob.append(0)
    total = 12 + 8 + len(json_bytes) + 8 + len(blob)
    out = bytearray()
    out += struct.pack("<III", 0x46546C67, 2, total)
    out += struct.pack("<I4s", len(json_bytes), b"JSON")
    out += json_bytes
    out += struct.pack("<I4s", len(blob), b"BIN\x00")
    out += blob
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(out)


def read_positions(path: Path, mesh_index: int) -> np.ndarray:
    data = path.read_bytes()
    json_len = struct.unpack_from("<I", data, 12)[0]
    gltf = json.loads(data[20 : 20 + json_len])
    bin_off = 20 + json_len
    bin_len = struct.unpack_from("<I", data, bin_off)[0]
    blob = data[bin_off + 8 : bin_off + 8 + bin_len]
    primitive = gltf["meshes"][mesh_index]["primitives"][0]
    accessor = gltf["accessors"][primitive["attributes"]["POSITION"]]
    view = gltf["bufferViews"][accessor["bufferView"]]
    start = view["byteOffset"]
    count = accessor["count"]
    return np.frombuffer(blob[start : start + count * 12], np.float32).reshape(-1, 3).copy()


def moved(point, origin, axis, degrees: float = 15.0) -> np.ndarray:
    return rodrigues(point, origin, axis, degrees) - point


def shoulder_anchors(parts: list[dict], center: np.ndarray) -> dict:
    """Joint centres in the uncentered glTF frame, then shifted with the meshes.

    +X is anatomical left and the midline is x≈0, so the left clavicle's
    medial end is the endpoint with the smaller X. That test has to happen
    before the shoulder group is recentered.
    """
    by_fj = {part["fj"]: part for part in parts}
    clavicle = to_gltf(by_fj["FJ6347"]["vertices"])
    scapula = to_gltf(by_fj["FJ3279"]["vertices"])
    humerus = to_gltf(by_fj["FJ6373"]["vertices"])

    end_a, end_b = endpoints(clavicle)
    medial, lateral = (end_a, end_b) if end_a[0] < end_b[0] else (end_b, end_a)
    shaft_a, shaft_b = endpoints(humerus)
    scapula_center = scapula.mean(axis=0)
    if np.linalg.norm(shaft_a - scapula_center) <= np.linalg.norm(shaft_b - scapula_center):
        proximal, distal = shaft_a, shaft_b
    else:
        proximal, distal = shaft_b, shaft_a
    head_points = humerus[np.linalg.norm(humerus - proximal, axis=1) < 0.045]
    if len(head_points) < 30:
        raise SystemExit("humeral head sample is too small")
    head = sphere_center(head_points)
    radius = float(np.linalg.norm(head_points - head, axis=1).mean())
    glenoid = closest_vertex(scapula, head)
    superior = clavicle[int(np.argmax(clavicle[:, 1]))]

    elev_axis = axis_that_increases(lateral, medial, (0.0, 0.0, 1.0), lambda p: p[1])
    protr_axis = axis_that_increases(lateral, medial, (0.0, 1.0, 0.0), lambda p: p[2])
    axial_axis = axis_that_increases(superior, medial, lateral - medial, lambda p: -p[2])
    normal = pca_small(scapula)
    if normal[2] > 0:
        normal = -normal
    scap_up = axis_that_increases(glenoid, lateral, normal, lambda p: p[1])
    scap_ir = axis_that_increases(glenoid, lateral, (0.0, 1.0, 0.0), lambda p: p[2])
    bone_dir = unit(distal - head)
    lift_dir = unit((1.0, 0.35, 0.55))
    abd_axis = axis_that_increases(distal, head, np.cross(bone_dir, lift_dir), lambda p: p[1])
    flex_axis = axis_that_increases(distal, head, np.cross(bone_dir, (0.0, 0.0, 1.0)), lambda p: p[2])

    ac_gap = float(np.linalg.norm(closest_vertex(scapula, lateral) - lateral))
    surface_gap = float(np.linalg.norm(closest_vertex(humerus, glenoid) - glenoid))
    socket = float(np.linalg.norm(head - glenoid))
    print(
        f"head radius {radius:.4f} m socket {socket:.4f} m "
        f"surface gap {surface_gap:.4f} m ac gap {ac_gap:.4f} m"
    )
    print("abd delta", r6(moved(distal, head, abd_axis)), "flex delta", r6(moved(distal, head, flex_axis)))
    print("elev delta", r6(moved(lateral, medial, elev_axis)), "protr delta", r6(moved(lateral, medial, protr_axis)))
    if ac_gap > 0.012 or surface_gap > 0.008 or not 0.015 < radius < 0.035:
        raise SystemExit("shoulder joints do not sit in the anatomical position")
    if moved(distal, head, abd_axis)[0] <= 0 or moved(distal, head, flex_axis)[2] <= 0:
        raise SystemExit("arm axes point the wrong way")

    medial = medial - center
    lateral = lateral - center
    head = head - center
    return {
        "medial": r6(medial),
        "lateral": r6(lateral),
        "head": r6(head),
        "elevAxis": r6(elev_axis),
        "protrAxis": r6(protr_axis),
        "axialAxis": r6(axial_axis),
        "scapUpAxis": r6(scap_up),
        "scapIRAxis": r6(scap_ir),
        "abdAxis": r6(abd_axis),
        "flexAxis": r6(flex_axis),
    }


def main(argv: list[str]) -> None:
    if len(argv) != 2:
        raise SystemExit("usage: build_skeleton_glbs.py objs_dir")
    folder = Path(argv[1])
    parts = select_parts(folder)
    expect_counts(parts)
    transformed = [to_gltf(part["vertices"]) for part in parts]
    lo = np.min([item.min(axis=0) for item in transformed], axis=0)
    hi = np.max([item.max(axis=0) for item in transformed], axis=0)
    center = (lo + hi) / 2.0
    print("skeleton center m", r6(center), "size m", r6(hi - lo))

    meshes = [prepare_mesh(part, center) for part in parts]
    write_glb(SKELETON_OUT, meshes)
    check = read_positions(SKELETON_OUT, 0)
    original = meshes[0]["vertices"]
    err = float(np.max(np.abs(check - original)))
    if err > 1e-5:
        raise SystemExit(f"GLB round-trip moved vertices by {err}")

    shoulder_parts = [part for part in parts if part["fj"] in set(SHOULDER_FJ.values())]
    shoulder_tx = [to_gltf(part["vertices"]) for part in shoulder_parts]
    slo = np.min([item.min(axis=0) for item in shoulder_tx], axis=0)
    shi = np.max([item.max(axis=0) for item in shoulder_tx], axis=0)
    shoulder_center = (slo + shi) / 2.0
    anchors = shoulder_anchors(shoulder_parts, shoulder_center)
    order = {"FJ6347": 0, "FJ3279": 1, "FJ6373": 2}
    shoulder_parts.sort(key=lambda part: order[part["fj"]])
    shoulder_meshes = [prepare_mesh(part, shoulder_center) for part in shoulder_parts]
    write_glb(SHOULDER_OUT, shoulder_meshes, {"anchors": anchors})

    sources = []
    for part in sorted(parts, key=lambda item: item["id"]):
        sources.append(
            {
                "id": part["id"],
                "zh": part["zh"],
                "en": part["name"],
                "fj": part["fj"],
                "bp": part["bp"],
                "fma": part["fma"],
                "sha256": part["sha256"],
                "lesson": part["lesson"],
                "vertices": int(len(part["vertices"])),
            }
        )
    SOURCES_OUT.write_text(json.dumps(sources, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(
        f"skeleton {SKELETON_OUT.stat().st_size} bytes, "
        f"shoulder {SHOULDER_OUT.stat().st_size} bytes, "
        f"verts {sum(len(part['vertices']) for part in parts)}"
    )


if __name__ == "__main__":
    main(sys.argv)
