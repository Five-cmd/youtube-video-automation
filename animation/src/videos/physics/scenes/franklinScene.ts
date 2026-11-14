// Modular 3D environment for FranklinShort:
// 1752 Philadelphia colonial courtyard, gabled timber shed, brick townhouse backdrop,
// layered storm clouds, colonial fence, and wet flagstone ground.
import * as THREE from "three";
import { twoTone } from "../../bridge/shade";

export function buildFranklinPiazza(stageGroup: THREE.Group, mats: Record<string, THREE.Material>) {
  const g = new THREE.Group();

  const wetStone = twoTone(new THREE.MeshLambertMaterial({ color: "#4e5664" }));
  const curbMat = twoTone(new THREE.MeshLambertMaterial({ color: "#6e737c" }));
  const brickMat = twoTone(new THREE.MeshLambertMaterial({ color: "#7c3b2e" }));
  const trimMat = twoTone(new THREE.MeshLambertMaterial({ color: "#d7d0c2" }));
  const slateMat = twoTone(new THREE.MeshLambertMaterial({ color: "#2d333d" }));
  const cloudMat = twoTone(new THREE.MeshLambertMaterial({ color: "#364050" }));
  const cloudRimMat = twoTone(new THREE.MeshLambertMaterial({ color: "#526075" }));

  // Wet cobblestone courtyard floor + raised outer curb
  const floor = new THREE.Mesh(new THREE.BoxGeometry(18, 0.14, 18), wetStone);
  floor.position.set(0, -0.07, -1.5);
  g.add(floor);

  for (let i = -3; i <= 3; i++) {
    const seamX = new THREE.Mesh(new THREE.BoxGeometry(16, 0.02, 0.08), curbMat);
    seamX.position.set(0, 0.01, i * 2.2 - 1.5);
    const seamZ = new THREE.Mesh(new THREE.BoxGeometry(0.08, 0.02, 16), curbMat);
    seamZ.position.set(i * 2.2, 0.01, -1.5);
    g.add(seamX, seamZ);
  }

  // Gabled timber shed roof & side beams around Franklin's shelter (centered at x=0.65, z=-0.35)
  const gableL = new THREE.Mesh(new THREE.BoxGeometry(1.15, 0.1, 1.75), slateMat);
  gableL.position.set(0.2, 2.74, -0.35);
  gableL.rotation.z = 0.44;
  const gableR = new THREE.Mesh(new THREE.BoxGeometry(1.15, 0.1, 1.75), slateMat);
  gableR.position.set(1.1, 2.74, -0.35);
  gableR.rotation.z = -0.44;
  const ridge = new THREE.Mesh(new THREE.BoxGeometry(0.16, 0.14, 1.82), mats.wood);
  ridge.position.set(0.65, 2.98, -0.35);
  g.add(gableL, gableR, ridge);

  // Back wall of the shed with shuttered window
  const backWall = new THREE.Mesh(new THREE.BoxGeometry(1.72, 2.35, 0.14), mats.wood);
  backWall.position.set(0.65, 1.18, -1.06);
  const sill = new THREE.Mesh(new THREE.BoxGeometry(0.66, 0.08, 0.2), trimMat);
  sill.position.set(0.65, 1.25, -1.0);
  g.add(backWall, sill);

  // Colonial brick townhouse row in the background (z = -6.8)
  for (const [bx, bw, bh] of [[-4.8, 3.4, 5.2], [-1.2, 3.6, 6.0], [2.8, 3.8, 5.4], [6.6, 3.2, 4.9]] as const) {
    const house = new THREE.Mesh(new THREE.BoxGeometry(bw, bh, 2.8), brickMat);
    house.position.set(bx, bh / 2, -6.8);
    const roof = new THREE.Mesh(new THREE.ConeGeometry(bw * 0.72, 1.6, 4), slateMat);
    roof.rotation.y = Math.PI / 4;
    roof.position.set(bx, bh + 0.75, -6.8);
    const cornice = new THREE.Mesh(new THREE.BoxGeometry(bw + 0.18, 0.18, 2.95), trimMat);
    cornice.position.set(bx, bh, -6.8);
    g.add(house, roof, cornice);

    // Warm candlelit windows
    for (const wy of [1.8, 3.6]) {
      if (wy > bh - 0.8) continue;
      for (const wx of [-bw * 0.25, bw * 0.25]) {
        const win = new THREE.Mesh(new THREE.BoxGeometry(0.55, 0.82, 0.08), mats.gold);
        win.position.set(bx + wx, wy, -5.36);
        g.add(win);
      }
    }
  }

  // Colonial picket fence & iron streetlamp posts
  for (let fx = -6.5; fx <= 6.5; fx += 1.3) {
    if (Math.abs(fx - 0.6) < 1.6) continue;
    const post = new THREE.Mesh(new THREE.BoxGeometry(0.14, 1.1, 0.14), trimMat);
    post.position.set(fx, 0.55, -3.5);
    g.add(post);
  }
  const rail = new THREE.Mesh(new THREE.BoxGeometry(13.2, 0.08, 0.08), trimMat);
  rail.position.set(0, 0.85, -3.5);
  g.add(rail);

  for (const lx of [-3.6, 3.8]) {
    const lp = new THREE.Mesh(new THREE.CylinderGeometry(0.06, 0.1, 2.6, 8), mats.iron);
    lp.position.set(lx, 1.3, -2.8);
    const lantern = new THREE.Mesh(new THREE.BoxGeometry(0.26, 0.34, 0.26), mats.gold);
    lantern.position.set(lx, 2.72, -2.8);
    g.add(lp, lantern);
  }

  // Layered thunderstorm cloud canopy high overhead (y = 6.2..7.6)
  for (const [cx, cy, cz, sx, sy, sz] of [
    [-3.8, 6.6, -3.2, 3.4, 1.1, 2.8],
    [0.2, 7.1, -3.8, 4.2, 1.3, 3.2],
    [4.2, 6.7, -3.0, 3.6, 1.1, 2.8],
    [-1.8, 6.4, -1.2, 2.9, 0.9, 2.4],
    [2.4, 6.5, -1.4, 3.1, 0.95, 2.4],
  ] as const) {
    const puff = new THREE.Mesh(new THREE.SphereGeometry(1, 14, 10), cloudMat);
    puff.scale.set(sx, sy, sz);
    puff.position.set(cx, cy, cz);
    const rim = new THREE.Mesh(new THREE.SphereGeometry(1, 12, 8), cloudRimMat);
    rim.scale.set(sx * 0.85, sy * 0.55, sz * 0.85);
    rim.position.set(cx, cy - sy * 0.35, cz + 0.2);
    g.add(puff, rim);
  }

  stageGroup.add(g);
}
