// Modular 3D environment for RontgenShort:
// 1895 Wurzburg physics laboratory, dark oak floor, wainscoted walls, blackout curtains,
// Ruhmkorff induction coil, wooden screen easel, and 5-finger skeletal hand + wedding ring.
import * as THREE from "three";
import { NOINK } from "../../bridge/ink";
import { twoTone } from "../../bridge/shade";

export function buildRontgenLab(
  stageGroup: THREE.Group,
  bonesOverlay: THREE.Mesh,
  mats: Record<string, THREE.Material>
) {
  const g = new THREE.Group();

  const oakFloor = twoTone(new THREE.MeshLambertMaterial({ color: "#3d2c20" }));
  const wainscot = twoTone(new THREE.MeshLambertMaterial({ color: "#4f3728" }));
  const plaster = twoTone(new THREE.MeshLambertMaterial({ color: "#5e626c" }));
  const curtain = twoTone(new THREE.MeshLambertMaterial({ color: "#232633" }));
  const boneMat = new THREE.MeshBasicMaterial({ color: new THREE.Color(0.06, 0.22, 0.1) });
  const ringMat = new THREE.MeshBasicMaterial({ color: new THREE.Color(0.02, 0.08, 0.04) });

  // Oak laboratory floor
  const floor = new THREE.Mesh(new THREE.BoxGeometry(14, 0.14, 14), oakFloor);
  floor.position.set(0, -0.07, -1.5);
  g.add(floor);

  // Back lab wall with wainscot paneling (behind darkScreenWall at z=-1.8)
  const backWall = new THREE.Mesh(new THREE.BoxGeometry(12, 4.8, 0.2), plaster);
  backWall.position.set(0, 2.4, -3.4);
  const backWainscot = new THREE.Mesh(new THREE.BoxGeometry(12, 1.25, 0.24), wainscot);
  backWainscot.position.set(0, 0.62, -3.38);
  g.add(backWall, backWainscot);

  // Side walls with blackout-curtained tall lab windows
  for (const sx of [-4.4, 4.4]) {
    const sw = new THREE.Mesh(new THREE.BoxGeometry(0.2, 4.8, 10), plaster);
    sw.position.set(sx, 2.4, -1.2);
    const cur = new THREE.Mesh(new THREE.BoxGeometry(0.26, 2.6, 1.8), curtain);
    cur.position.set(sx > 0 ? sx - 0.12 : sx + 0.12, 2.2, -1.2);
    g.add(sw, cur);
  }

  // Brass Ruhmkorff induction coil & glass Crookes tube details on left workbench (x=-1.15, z=-0.45)
  const coil = new THREE.Mesh(new THREE.CylinderGeometry(0.18, 0.18, 0.56, 12), mats.copper);
  coil.rotation.z = Math.PI / 2;
  coil.position.set(-1.15, 1.8, -0.45);
  const crookesGlow = new THREE.Mesh(
    new THREE.SphereGeometry(0.16, 12, 10),
    new THREE.MeshBasicMaterial({ color: new THREE.Color(0.9, 3.2, 1.4) })
  );
  crookesGlow.position.set(-0.55, 1.38, -0.4);
  crookesGlow.layers.set(NOINK);
  g.add(coil, crookesGlow);

  // Wooden tripod stand under fluorescent screen (x=1.1, z=-0.35)
  const post = new THREE.Mesh(new THREE.CylinderGeometry(0.05, 0.07, 0.9, 8), mats.wood);
  post.position.set(1.1, 0.45, -0.35);
  const base = new THREE.Mesh(new THREE.CylinderGeometry(0.32, 0.38, 0.08, 12), mats.wood);
  base.position.set(1.1, 0.04, -0.35);
  g.add(post, base);

  // Add 5 skeletal fingers + wedding ring onto bonesOverlay (which sits at x=1.08, y=1.35, z=-0.35)
  for (let i = 0; i < 5; i++) {
    const fz = -0.16 + i * 0.08;
    const fl = i === 0 ? 0.24 : i === 2 ? 0.42 : 0.36;
    const finger = new THREE.Mesh(new THREE.BoxGeometry(0.04, fl, 0.042), boneMat);
    finger.position.set(-0.08, 0.24 + fl * 0.35, fz);
    if (i === 0) finger.rotation.x = -0.38;
    bonesOverlay.add(finger);
  }
  const ring = new THREE.Mesh(new THREE.TorusGeometry(0.045, 0.015, 6, 12), ringMat);
  ring.rotation.z = Math.PI / 2;
  ring.position.set(-0.08, 0.36, 0.08);
  bonesOverlay.add(ring);

  stageGroup.add(g);
}
