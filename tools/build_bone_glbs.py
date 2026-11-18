#!/usr/bin/env python3
"""Turn BodyParts3D 4.3 element OBJs into the lesson GLBs.

The site does not run this script. It records the only changes made to the
meshes: a rigid move to the origin, millimetres to metres, a fixed axis
change into glTF Y-up, and smooth vertex normals plus an ivory material.
Vertex positions are not smoothed, decimated, or remodelled.

Expected downloads (Anatomography 4.3, lifesciencedb.jp/bp3d/download.cgi):

  Left clavicle  FJ6347  BP23283  FMA13323  "Left clavicle"
  Left scapula   FJ3279  BP23279  FMA13396  "Left scapula"

Usage:
  python3 tools/build_bone_glbs.py clavicle.obj scapula.obj
"""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

import numpy as np
import trimesh
from trimesh.visual.material import PBRMaterial

ROOT = Path(__file__).resolve().parents[1]
OUT = {
    "clavicle": ROOT / "models" / "clavicle-left.glb",
    "scapula": ROOT / "models" / "scapula-left.glb",
}

BONE = PBRMaterial(
    name="bone",
    baseColorFactor=[0.90, 0.84, 0.73, 1.0],
    metallicFactor=0.0,
    roughnessFactor=0.62,
    doubleSided=False,
)


def load_obj(path: Path) -> trimesh.Trimesh:
    mesh = trimesh.load(path, process=False, force="mesh")
    if not isinstance(mesh, trimesh.Trimesh):
        raise SystemExit(f"{path} did not load as a single mesh")
    mesh.remove_unreferenced_vertices()
    # BodyParts3D winding is consistent. Flip only if normals point inward.
    centers = mesh.triangles_center - mesh.centroid
    if float(np.sum(centers * mesh.face_normals)) < 0:
        mesh.invert()
    return mesh


def orthonormal(z_axis: np.ndarray, up_hint: np.ndarray) -> np.ndarray:
    """Rows are glTF X, Y, Z expressed in the source coordinate system."""
    z_axis = np.asarray(z_axis, dtype=np.float64)
    z_axis /= np.linalg.norm(z_axis)
    up = np.asarray(up_hint, dtype=np.float64)
    up = up - z_axis * np.dot(up, z_axis)
    up /= np.linalg.norm(up)
    x_axis = np.cross(up, z_axis)
    x_axis /= np.linalg.norm(x_axis)
    return np.stack([x_axis, up, z_axis], axis=0)


def scapula_posterior(vertices: np.ndarray) -> np.ndarray:
    """Thin-axis direction that faces the scapular spine.

    The least-variance axis is the blade's thickness. Rendering both signs
    showed the spine, acromion, and infraspinous fossa on the side whose
    axis has a positive anatomical Y component. The eigenvector sign from
    a solver is not stable, so the Y component picks the sign.
    """
    centered = vertices - vertices.mean(axis=0)
    _, eigvec = np.linalg.eigh(np.cov(centered.T))
    normal = eigvec[:, 0]
    if normal[1] < 0:
        normal = -normal
    return normal


def orient(mesh: trimesh.Trimesh, kind: str) -> trimesh.Trimesh:
    vertices = np.asarray(mesh.vertices, dtype=np.float64)
    if kind == "clavicle":
        # Source Z is superior, X is the long axis, Y carries the S-curve.
        # glTF +Z then holds the S-curve, so a high camera sees it.
        rotation = orthonormal([0.0, 1.0, 0.0], [0.0, 0.0, 1.0])
    elif kind == "scapula":
        rotation = orthonormal(scapula_posterior(vertices), [0.0, 0.0, 1.0])
    else:
        raise SystemExit(f"unknown kind {kind}")
    center = (vertices.min(axis=0) + vertices.max(axis=0)) / 2.0
    transformed = (vertices - center) @ rotation.T
    transformed -= (transformed.min(axis=0) + transformed.max(axis=0)) / 2.0
    transformed *= 0.001
    out = trimesh.Trimesh(vertices=transformed, faces=mesh.faces, process=False)
    out.visual = trimesh.visual.TextureVisuals(material=BONE)
    # Touch so the exporter writes smooth normals instead of flat faces.
    _ = out.vertex_normals
    return out


def main(argv: list[str]) -> None:
    if len(argv) != 3:
        raise SystemExit("usage: build_bone_glbs.py clavicle.obj scapula.obj")
    sources = {"clavicle": Path(argv[1]), "scapula": Path(argv[2])}
    for kind, path in sources.items():
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        mesh = orient(load_obj(path), kind)
        OUT[kind].parent.mkdir(parents=True, exist_ok=True)
        mesh.export(OUT[kind])
        loaded = trimesh.load(OUT[kind], force="mesh")
        print(
            f"{kind}: src {path.name} sha256 {digest} "
            f"verts {len(mesh.vertices)} faces {len(mesh.faces)} "
            f"glb {OUT[kind].stat().st_size} bytes "
            f"reload verts {len(loaded.vertices)} "
            f"extents_m {np.round(loaded.extents, 4).tolist()}"
        )


if __name__ == "__main__":
    main(sys.argv)
