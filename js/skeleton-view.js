import {
  Box3,
  BufferAttribute,
  BufferGeometry,
  Mesh,
  MeshStandardMaterial,
  Vector3,
  DoubleSide,
} from "./vendor/three.module.min.js";
import { loadGlb } from "./glb.js";
import { createStage } from "./stage.js";
import { createOrbit, bindCanvas } from "./orbit.js";

const IVORY = [0.9, 0.84, 0.73];
const HOT = [0.93, 0.62, 0.48];

const canvas = document.querySelector("#view");
const status = document.querySelector("#stage-status");
const note = document.querySelector("#bone-note");
const error = document.querySelector("#viewer-error");

function fail() {
  if (status) status.hidden = true;
  if (error) error.hidden = false;
}

function paint(colors, part, rgb) {
  const end = (part.firstVertex + part.vertexCount) * 3;
  for (let i = part.firstVertex * 3; i < end; i += 3) {
    colors[i] = rgb[0];
    colors[i + 1] = rgb[1];
    colors[i + 2] = rgb[2];
  }
}

function partAt(parts, faceIndex) {
  let lo = 0;
  let hi = parts.length - 1;
  while (lo <= hi) {
    const mid = (lo + hi) >> 1;
    const part = parts[mid];
    if (faceIndex < part.firstFace) hi = mid - 1;
    else if (faceIndex >= part.firstFace + part.faceCount) lo = mid + 1;
    else return part;
  }
  return null;
}

async function main() {
  let stage;
  try {
    stage = createStage(canvas);
  } catch (err) {
    fail();
    return;
  }
  if (!stage.renderer.getContext()) {
    fail();
    return;
  }

  let loaded;
  try {
    loaded = await loadGlb("models/skeleton.glb");
  } catch (err) {
    fail();
    return;
  }

  let vertexCount = 0;
  let indexCount = 0;
  loaded.meshes.forEach((mesh) => {
    vertexCount += mesh.position.length / 3;
    indexCount += mesh.index.length;
  });

  const position = new Float32Array(vertexCount * 3);
  const normal = new Float32Array(vertexCount * 3);
  const color = new Float32Array(vertexCount * 3);
  const index = new Uint32Array(indexCount);
  const parts = [];
  let vertexBase = 0;
  let indexBase = 0;

  loaded.meshes.forEach((mesh) => {
    const count = mesh.position.length / 3;
    const faces = mesh.index.length / 3;
    position.set(mesh.position, vertexBase * 3);
    normal.set(mesh.normal, vertexBase * 3);
    for (let i = 0; i < count; i += 1) {
      color[(vertexBase + i) * 3] = IVORY[0];
      color[(vertexBase + i) * 3 + 1] = IVORY[1];
      color[(vertexBase + i) * 3 + 2] = IVORY[2];
    }
    for (let i = 0; i < mesh.index.length; i += 1) {
      index[indexBase + i] = mesh.index[i] + vertexBase;
    }
    parts.push({
      firstFace: indexBase / 3,
      faceCount: faces,
      firstVertex: vertexBase,
      vertexCount: count,
      zh: mesh.extras.zh || mesh.name,
      lesson: mesh.extras.lesson || "",
    });
    vertexBase += count;
    indexBase += mesh.index.length;
  });

  const geometry = new BufferGeometry();
  geometry.setAttribute("position", new BufferAttribute(position, 3));
  geometry.setAttribute("normal", new BufferAttribute(normal, 3));
  geometry.setAttribute("color", new BufferAttribute(color, 3));
  geometry.setIndex(new BufferAttribute(index, 1));
  const body = new Mesh(
    geometry,
    new MeshStandardMaterial({
      color: 0xffffff,
      vertexColors: true,
      roughness: 0.62,
      metalness: 0,
      side: DoubleSide,
    })
  );
  stage.scene.add(body);

  const box = new Box3().setFromObject(body);
  const size = box.getSize(new Vector3());
  const center = box.getCenter(new Vector3());
  stage.resize();
  const fov = (stage.camera.fov * Math.PI) / 180;
  const distY = (size.y * 0.55) / Math.tan(fov / 2);
  const distX = (size.x * 0.62) / (Math.tan(fov / 2) * stage.camera.aspect);
  const radius = Math.max(distY, distX) * 1.06;
  const orbit = createOrbit(stage.camera, center, {
    theta: 0,
    phi: Math.PI / 2,
    radius,
    minRadius: radius * 0.35,
    maxRadius: radius * 3.2,
  });
  orbit.apply();
  if (status) status.hidden = true;
  stage.draw();

  let selected = null;
  const colors = geometry.getAttribute("color");

  function highlight(part) {
    if (selected) paint(colors.array, selected, IVORY);
    if (part) paint(colors.array, part, HOT);
    selected = part;
    colors.needsUpdate = true;
    stage.draw();
  }

  bindCanvas(canvas, {
    onDrag(dx, dy) {
      orbit.rotate(dx, dy);
      stage.draw();
    },
    onZoom(factor) {
      orbit.zoom(factor);
      stage.draw();
    },
    onTap(event) {
      const hits = stage.hit(event, body);
      if (!hits.length) {
        highlight(null);
        note.textContent = "";
        return;
      }
      const part = partAt(parts, hits[0].faceIndex);
      if (!part) return;
      highlight(part);
      if (part.lesson) {
        window.location.href = part.lesson;
        return;
      }
      note.textContent = part.zh + "，这一课还没开";
    },
  });
}

main();
