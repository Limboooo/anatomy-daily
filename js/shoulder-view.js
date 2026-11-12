import {
  Box3,
  BufferAttribute,
  BufferGeometry,
  Group,
  Mesh,
  MeshStandardMaterial,
  Quaternion,
  Vector3,
  DoubleSide,
} from "./vendor/three.module.min.js";
import { loadGlb } from "./glb.js";
import { createStage } from "./stage.js";
import { createOrbit, bindCanvas } from "./orbit.js";

const BONE = new Vector3(0.9, 0.84, 0.73);
const LIMITS = {
  elev: [-6, 28],
  protr: [-12, 18],
  axial: [-4, 18],
  scapUp: [-4, 36],
  scapIR: [-10, 14],
  abd: [0, 80],
  flex: [-18, 40],
};
const NAME = {
  "left-clavicle": "锁骨",
  "left-scapula": "肩胛骨",
  "left-humerus": "肱骨",
};

const canvas = document.querySelector("#view");
const status = document.querySelector("#stage-status");
const note = document.querySelector("#bone-note");
const error = document.querySelector("#viewer-error");
const reset = document.querySelector("#reset");

function fail() {
  if (status) status.hidden = true;
  if (error) error.hidden = false;
}

function clamp(name, value) {
  const pair = LIMITS[name];
  return Math.min(pair[1], Math.max(pair[0], value));
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
    loaded = await loadGlb("models/shoulder-left.glb");
  } catch (err) {
    fail();
    return;
  }
  const anchors = loaded.sceneExtras.anchors;
  if (!anchors) {
    fail();
    return;
  }

  const byName = {};
  loaded.meshes.forEach((mesh) => {
    byName[mesh.name] = mesh;
  });
  const materials = {};

  function makeMesh(id) {
    const source = byName[id];
    const geometry = new BufferGeometry();
    geometry.setAttribute("position", new BufferAttribute(source.position, 3));
    geometry.setAttribute("normal", new BufferAttribute(source.normal, 3));
    geometry.setIndex(new BufferAttribute(source.index, 1));
    const material = new MeshStandardMaterial({
      color: BONE,
      roughness: 0.62,
      metalness: 0,
      side: DoubleSide,
    });
    materials[id] = material;
    const mesh = new Mesh(geometry, material);
    mesh.name = id;
    return mesh;
  }

  const medial = new Vector3().fromArray(anchors.medial);
  const lateral = new Vector3().fromArray(anchors.lateral);
  const head = new Vector3().fromArray(anchors.head);

  // Sternoclavicular pivot. Axial twist spins only the clavicle, so the
  // acromioclavicular joint stays put while the clavicle rolls.
  const scPivot = new Group();
  scPivot.position.copy(medial);
  const clavicleSpin = new Group();
  const clavicle = makeMesh("left-clavicle");
  clavicle.position.copy(medial).multiplyScalar(-1);
  clavicleSpin.add(clavicle);
  const acPivot = new Group();
  acPivot.position.copy(lateral).sub(medial);
  const scapulaPivot = new Group();
  const scapula = makeMesh("left-scapula");
  scapula.position.copy(lateral).multiplyScalar(-1);
  const ghPivot = new Group();
  ghPivot.position.copy(head).sub(lateral);
  const humerus = makeMesh("left-humerus");
  humerus.position.copy(head).multiplyScalar(-1);
  ghPivot.add(humerus);
  scapulaPivot.add(scapula, ghPivot);
  acPivot.add(scapulaPivot);
  scPivot.add(clavicleSpin, acPivot);
  stage.scene.add(scPivot);

  const pose = { elev: 0, protr: 0, axial: 0, scapUp: 0, scapIR: 0, abd: 0, flex: 0 };
  const q1 = new Quaternion();
  const q2 = new Quaternion();
  const axis = new Vector3();

  function fromAxis(target, values, degrees) {
    target.setFromAxisAngle(axis.fromArray(values).normalize(), (degrees * Math.PI) / 180);
    return target;
  }

  function applyPose() {
    fromAxis(q1, anchors.protrAxis, pose.protr);
    fromAxis(q2, anchors.elevAxis, pose.elev);
    scPivot.quaternion.copy(q1).multiply(q2);
    fromAxis(clavicleSpin.quaternion, anchors.axialAxis, pose.axial);
    fromAxis(q1, anchors.scapIRAxis, pose.scapIR);
    fromAxis(q2, anchors.scapUpAxis, pose.scapUp);
    scapulaPivot.quaternion.copy(q1).multiply(q2);
    fromAxis(q1, anchors.flexAxis, pose.flex);
    fromAxis(q2, anchors.abdAxis, pose.abd);
    ghPivot.quaternion.copy(q1).multiply(q2);
  }

  function addCoupled(driver, dx, dy) {
    if (driver === "left-clavicle") {
      const lift = -dy * 0.18;
      pose.elev = clamp("elev", pose.elev + lift);
      pose.protr = clamp("protr", pose.protr + dx * 0.12);
      pose.axial = clamp("axial", pose.axial + lift * 0.45);
      pose.scapUp = clamp("scapUp", pose.scapUp + lift * 0.55);
    } else if (driver === "left-scapula") {
      const lift = -dy * 0.2;
      pose.scapUp = clamp("scapUp", pose.scapUp + lift);
      pose.scapIR = clamp("scapIR", pose.scapIR + dx * 0.1);
      pose.elev = clamp("elev", pose.elev + lift * 0.6);
      pose.axial = clamp("axial", pose.axial + lift * 0.35);
      pose.protr = clamp("protr", pose.protr + dx * 0.1);
    } else if (driver === "left-humerus") {
      const lift = -dy * 0.22;
      pose.abd = clamp("abd", pose.abd + lift);
      pose.flex = clamp("flex", pose.flex + dx * 0.12);
      const share = Math.max(0, Math.min(1, (pose.abd - 8) / 30));
      pose.scapUp = clamp("scapUp", pose.scapUp + lift * 0.85 * share);
      pose.elev = clamp("elev", pose.elev + lift * 0.55 * share);
      pose.axial = clamp("axial", pose.axial + lift * 0.35 * share);
      pose.protr = clamp("protr", pose.protr + dx * 0.08);
      pose.scapIR = clamp("scapIR", pose.scapIR + dx * 0.05);
    }
    applyPose();
  }

  const box = new Box3().setFromObject(scPivot);
  const size = box.getSize(new Vector3());
  const center = box.getCenter(new Vector3());
  stage.resize();
  const fov = (stage.camera.fov * Math.PI) / 180;
  const distY = (size.y * 0.62) / Math.tan(fov / 2);
  const distX = (size.x * 0.7) / (Math.tan(fov / 2) * stage.camera.aspect);
  const radius = Math.max(distY, distX) * 1.15;
  const orbit = createOrbit(stage.camera, center, {
    theta: 0.55,
    phi: Math.PI / 2 - 0.12,
    radius,
    minRadius: radius * 0.4,
    maxRadius: radius * 3,
  });
  applyPose();
  orbit.apply();
  if (status) status.hidden = true;
  stage.draw();

  let grabbed = null;

  function highlight(name) {
    Object.keys(materials).forEach((id) => {
      materials[id].emissive.setHex(id === name ? 0x4a2e22 : 0x000000);
    });
  }

  bindCanvas(canvas, {
    onStart(event) {
      const hits = stage.hit(event, scPivot);
      grabbed = hits.length ? hits[0].object.name : null;
      highlight(grabbed);
      stage.draw();
    },
    onDrag(dx, dy) {
      if (grabbed) {
        addCoupled(grabbed, dx, dy);
        note.textContent = "正在拖" + NAME[grabbed] + "，另外两块跟着动";
      } else {
        orbit.rotate(dx, dy);
      }
      stage.draw();
    },
    onZoom(factor) {
      orbit.zoom(factor);
      stage.draw();
    },
    onTap() {
      if (grabbed) {
        note.textContent = "拖" + NAME[grabbed] + "，另外两块会跟着动";
      }
      stage.draw();
    },
  });

  reset.addEventListener("click", () => {
    Object.keys(pose).forEach((key) => {
      pose[key] = 0;
    });
    grabbed = null;
    highlight(null);
    applyPose();
    orbit.reset();
    note.textContent = "已回到解剖位置";
    stage.draw();
  });
}

main();
