// Minimal GLB reader for the meshes this site writes.
// Positions and normals are tightly packed, with no node transforms.

const COMPONENT = { 5123: Uint16Array, 5125: Uint32Array, 5126: Float32Array };
const WIDTH = { SCALAR: 1, VEC3: 3 };

export async function loadGlb(url) {
  const response = await fetch(url);
  if (!response.ok) throw new Error("glb");
  const buf = await response.arrayBuffer();
  const view = new DataView(buf);
  if (view.getUint32(0, true) !== 0x46546c67) throw new Error("glb");
  const jsonLen = view.getUint32(12, true);
  const json = JSON.parse(new TextDecoder().decode(new Uint8Array(buf, 20, jsonLen)));
  const binStart = 20 + jsonLen;
  const binLen = view.getUint32(binStart, true);
  const bin = new Uint8Array(buf, binStart + 8, binLen);

  function readAccessor(index) {
    const accessor = json.accessors[index];
    const bufferView = json.bufferViews[accessor.bufferView];
    const Ctor = COMPONENT[accessor.componentType];
    const count = accessor.count * WIDTH[accessor.type];
    const offset = (bufferView.byteOffset || 0) + (accessor.byteOffset || 0);
    const array = new Ctor(count);
    array.set(new Ctor(bin.buffer, bin.byteOffset + offset, count));
    return array;
  }

  const meshes = json.nodes.map((node) => {
    const primitive = json.meshes[node.mesh].primitives[0];
    return {
      name: node.name,
      extras: node.extras || {},
      position: readAccessor(primitive.attributes.POSITION),
      normal: readAccessor(primitive.attributes.NORMAL),
      index: readAccessor(primitive.indices),
    };
  });
  const scene = json.scenes && json.scenes[0];
  return { meshes, sceneExtras: (scene && scene.extras) || {} };
}
