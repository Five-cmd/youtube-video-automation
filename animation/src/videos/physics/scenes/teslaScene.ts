// Modular 3D environment for TeslaShort:
// 1901 Wardenclyffe Tower (Long Island), octagonal lattice legs, brick powerhouse lab,
// glowing copper ground coils, meadow grass, and perimeter iron fence.
import * as THREE from "three";
import { NOINK } from "../../bridge/ink";
import { twoTone } from "../../bridge/shade";

export function buildTeslaWardenclyffe(
  stageGroup: THREE.Group,
  towerGroup: THREE.Group,
  mats: Record<string, THREE.Material>
) {
  const g = new THREE.Group();

  const meadowMat = twoTone(new THREE.MeshLambertMaterial({ color: "#4b6b3c" }));
  const gravelMat = twoTone(new THREE.MeshLambertMaterial({ color: "#8b8579" }));
  const brickMat = twoTone(new THREE.MeshLambertMaterial({ color: "#8e4234" }));
  const slateMat = twoTone(new THREE.MeshLambertMaterial({ color: "#323741" }));
  const trimMat = twoTone(new THREE.MeshLambertMaterial({ color: "#d8d1c5" }));
  const coilGlow = new THREE.MeshBasicMaterial({ color: new THREE.Color(1.4, 2.5, 4.8) });

  // Long Island meadow ground + gravel path
  const meadow = new THREE.Mesh(new THREE.BoxGeometry(20, 0.14, 20), meadowMat);
  meadow.position.set(0, -0.07, -1.8);
  const path = new THREE.Mesh(new THREE.BoxGeometry(2.6, 0.03, 12), gravelMat);
  path.position.set(0.5, 0.01, -1.5);
  g.add(meadow, path);

  // Octagonal lattice tower struts + horizontal collars added directly to towerGroup (at [-0.95, 0, -0.95])
  for (let i = 0; i < 8; i++) {
    const a = (i / 8) * Math.PI * 2;
    const strut = new THREE.Mesh(new THREE.CylinderGeometry(0.038, 0.055, 2.85, 6), mats.wood);
    strut.position.set(Math.cos(a) * 0.42, 1.38, Math.sin(a) * 0.42);
    strut.rotation.z = Math.cos(a) * 0.16;
    strut.rotation.x = -Math.sin(a) * 0.16;
    towerGroup.add(strut);
  }
  for (const [ry, rr] of [[0.75, 0.56], [1.55, 0.44], [2.25, 0.34]] as const) {
    const collar = new THREE.Mesh(new THREE.TorusGeometry(rr, 0.035, 6, 16), mats.iron);
    collar.rotation.x = Math.PI / 2;
    collar.position.y = ry;
    towerGroup.add(collar);
  }
  // Glowing concentric copper ground-coil rings beneath the tower
  for (const cr of [0.85, 1.25]) {
    const ring = new THREE.Mesh(new THREE.TorusGeometry(cr, 0.025, 6, 24), coilGlow);
    ring.rotation.x = Math.PI / 2;
    ring.position.y = 0.03;
    ring.layers.set(NOINK);
    towerGroup.add(ring);
  }

  // 1901 Red-brick Wardenclyffe Powerhouse Laboratory behind tower (z = -6.2)
  const lab = new THREE.Mesh(new THREE.BoxGeometry(6.8, 2.8, 3.2), brickMat);
  lab.position.set(0.4, 1.4, -6.2);
  const labRoof = new THREE.Mesh(new THREE.BoxGeometry(7.2, 0.3, 3.5), slateMat);
  labRoof.position.set(0.4, 2.95, -6.2);
  const stack = new THREE.Mesh(new THREE.CylinderGeometry(0.24, 0.34, 4.4, 10), brickMat);
  stack.position.set(3.1, 2.2, -6.6);
  const stackCap = new THREE.Mesh(new THREE.CylinderGeometry(0.32, 0.32, 0.18, 10), trimMat);
  stackCap.position.set(3.1, 4.45, -6.6);
  g.add(lab, labRoof, stack, stackCap);

  // Arched glowing laboratory windows
  for (let wx = -2.0; wx <= 2.8; wx += 1.2) {
    const win = new THREE.Mesh(new THREE.BoxGeometry(0.62, 1.15, 0.08), mats.gold);
    win.position.set(wx, 1.45, -4.58);
    const frame = new THREE.Mesh(new THREE.BoxGeometry(0.72, 0.12, 0.12), trimMat);
    frame.position.set(wx, 0.86, -4.56);
    g.add(win, frame);
  }

  // Iron perimeter fence posts
  for (let fx = -6.0; fx <= 6.0; fx += 1.5) {
    if (Math.abs(fx - 0.5) < 1.3) continue;
    const post = new THREE.Mesh(new THREE.CylinderGeometry(0.05, 0.07, 0.95, 6), mats.iron);
    post.position.set(fx, 0.48, -3.4);
    g.add(post);
  }

  stageGroup.add(g);
}
