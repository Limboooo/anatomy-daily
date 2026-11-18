import {
  WebGLRenderer,
  Scene,
  PerspectiveCamera,
  HemisphereLight,
  DirectionalLight,
  SRGBColorSpace,
  NoToneMapping,
  Raycaster,
  Vector2,
} from "./vendor/three.module.min.js";

export function createStage(canvas) {
  const renderer = new WebGLRenderer({ canvas, antialias: true, alpha: false });
  renderer.outputColorSpace = SRGBColorSpace;
  renderer.toneMapping = NoToneMapping;
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
  renderer.setClearColor(0xeee8de, 1);
  const scene = new Scene();
  const camera = new PerspectiveCamera(28, 1, 0.02, 40);
  scene.add(new HemisphereLight(0xfff8ee, 0xd5c6b2, 0.95));
  const key = new DirectionalLight(0xffffff, 1.25);
  key.position.set(0.7, 1.5, 1.8);
  scene.add(key);
  const fill = new DirectionalLight(0xfff1e2, 0.4);
  fill.position.set(-1.1, 0.3, -0.6);
  scene.add(fill);
  const raycaster = new Raycaster();
  const pointer = new Vector2();

  function resize() {
    const width = canvas.clientWidth || 1;
    const height = canvas.clientHeight || 1;
    renderer.setSize(width, height, false);
    camera.aspect = width / height;
    camera.updateProjectionMatrix();
  }

  function draw() {
    renderer.render(scene, camera);
  }

  function hit(event, object) {
    const rect = canvas.getBoundingClientRect();
    pointer.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
    pointer.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
    raycaster.setFromCamera(pointer, camera);
    return raycaster.intersectObject(object, true);
  }

  window.addEventListener("resize", () => {
    resize();
    draw();
  });

  return { renderer, scene, camera, resize, draw, hit };
}
