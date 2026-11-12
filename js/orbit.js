import { Vector3 } from "./vendor/three.module.min.js";

function clamp(value, min, max) {
  return Math.min(max, Math.max(min, value));
}

export function createOrbit(camera, target, options) {
  const home = {
    theta: options.theta || 0,
    phi: options.phi,
    radius: options.radius,
  };
  const state = {
    theta: home.theta,
    phi: home.phi,
    radius: home.radius,
    minRadius: options.minRadius,
    maxRadius: options.maxRadius,
    target: target.clone(),
  };
  const offset = new Vector3();

  function apply() {
    const sin = Math.sin(state.phi);
    offset.set(
      state.radius * sin * Math.sin(state.theta),
      state.radius * Math.cos(state.phi),
      state.radius * sin * Math.cos(state.theta)
    );
    camera.position.copy(state.target).add(offset);
    camera.lookAt(state.target);
  }

  function rotate(dx, dy) {
    state.theta -= dx * 0.008;
    state.phi = clamp(state.phi + dy * 0.008, 0.18, Math.PI - 0.18);
    apply();
  }

  function zoom(factor) {
    state.radius = clamp(state.radius * factor, state.minRadius, state.maxRadius);
    apply();
  }

  function reset() {
    state.theta = home.theta;
    state.phi = home.phi;
    state.radius = home.radius;
    apply();
  }

  return { apply, rotate, zoom, reset };
}

export function bindCanvas(canvas, { onStart, onDrag, onTap, onZoom }) {
  const pointers = new Map();
  let pinch = 0;
  let dragId = null;
  let moved = 0;

  function separation() {
    const pts = [...pointers.values()];
    return Math.hypot(pts[0].x - pts[1].x, pts[0].y - pts[1].y);
  }

  canvas.addEventListener("pointerdown", (event) => {
    canvas.setPointerCapture(event.pointerId);
    pointers.set(event.pointerId, { x: event.clientX, y: event.clientY });
    if (pointers.size === 1) {
      dragId = event.pointerId;
      moved = 0;
      pinch = 0;
      if (onStart) onStart(event);
    } else if (pointers.size === 2) {
      pinch = separation();
      dragId = null;
    }
  });

  canvas.addEventListener("pointermove", (event) => {
    const prev = pointers.get(event.pointerId);
    if (!prev) return;
    const dx = event.clientX - prev.x;
    const dy = event.clientY - prev.y;
    pointers.set(event.pointerId, { x: event.clientX, y: event.clientY });
    if (pointers.size >= 2 && pinch) {
      const next = separation();
      if (next > 0) onZoom(pinch / next);
      pinch = next;
      return;
    }
    if (event.pointerId === dragId) {
      moved += Math.abs(dx) + Math.abs(dy);
      onDrag(dx, dy);
    }
  });

  function finish(event) {
    if (!pointers.has(event.pointerId)) return;
    pointers.delete(event.pointerId);
    if (pointers.size < 2) pinch = 0;
    if (event.pointerId === dragId) {
      if (moved < 8 && onTap) onTap(event);
      dragId = null;
    }
  }

  canvas.addEventListener("pointerup", finish);
  canvas.addEventListener("pointercancel", finish);
  canvas.addEventListener("wheel", (event) => {
    event.preventDefault();
    onZoom(Math.exp(event.deltaY * 0.0011));
  }, { passive: false });
  canvas.addEventListener("touchmove", (event) => event.preventDefault(), { passive: false });
}
