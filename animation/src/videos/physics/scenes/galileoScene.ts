// Modular 3D Environment Sets for GalileoShort:
//   1. 1589 Pisa Cathedral Piazza (travertine plaza, Tuscan colonnade arcade, cypress trees, 6-tier Leaning Tower)
//   2. True 3D Lunar Vacuum Dome at MY = 260 (360-deg starry space sphere, painted Earth, cratered regolith)
import * as THREE from "three";
import { NOINK } from "../../bridge/ink";
import { twoTone } from "../../bridge/shade";
import { ctex } from "../../bridge/paint";

export const MOON_Y = 260;

export type GalileoSceneMats = {
  stone: THREE.Material;
  paper: THREE.Material;
  iron: THREE.Material;
  wood: THREE.Material;
};

function starfieldTex(): THREE.Texture {
  return ctex("galileoStars", 512, 512, (g) => {
    g.fillStyle = "#040712";
    g.fillRect(0, 0, 512, 512);
    // Subtle milky-way glow band
    const gr = g.createLinearGradient(0, 80, 512, 420);
    gr.addColorStop(0, "rgba(25, 40, 85, 0)");
    gr.addColorStop(0.5, "rgba(55, 85, 145, 0.28)");
    gr.addColorStop(1, "rgba(25, 40, 85, 0)");
    g.fillStyle = gr;
    g.fillRect(0, 0, 512, 512);
    // Deterministic crisp stars
    let s = 1337;
    const rnd = () => {
      s = (s * 1664525 + 1013904223) >>> 0;
      return s / 4294967296;
    };
    for (let i = 0; i < 420; i++) {
      const x = rnd() * 512;
      const y = rnd() * 512;
      const r = rnd() < 0.12 ? 1.8 : rnd() < 0.4 ? 1.1 : 0.7;
      g.fillStyle = rnd() < 0.2 ? "#cfe4ff" : rnd() < 0.15 ? "#ffe9c4" : "#ffffff";
      g.beginPath();
      g.arc(x, y, r, 0, Math.PI * 2);
      g.fill();
    }
  });
}

function earthTex(): THREE.Texture {
  return ctex("galileoEarth", 256, 128, (g) => {
    g.fillStyle = "#1c5fb8";
    g.fillRect(0, 0, 256, 128);
    // Continents
    g.fillStyle = "#4fa35c";
    for (const [cx, cy, rx, ry] of [
      [68, 52, 24, 18],
      [96, 82, 16, 22],
      [162, 48, 32, 20],
      [190, 76, 18, 16],
      [140, 96, 14, 10],
    ]) {
      g.beginPath();
      g.ellipse(cx, cy, rx, ry, 0.25, 0, Math.PI * 2);
      g.fill();
    }
    // Cloud swirls
    g.fillStyle = "rgba(255, 255, 255, 0.65)";
    for (const [cx, cy, rx, ry] of [
      [52, 34, 28, 7],
      [120, 62, 36, 8],
      [182, 42, 30, 6],
      [88, 104, 34, 7],
      [210, 88, 22, 6],
    ]) {
      g.beginPath();
      g.ellipse(cx, cy, rx, ry, -0.15, 0, Math.PI * 2);
      g.fill();
    }
  });
}

export function buildGalileoPisaPiazza(stageGroup: THREE.Group, mats: GalileoSceneMats): THREE.Group {
  const towerGroup = new THREE.Group();
  const plazaMat = twoTone(new THREE.MeshLambertMaterial({ color: "#e5dcc9" }));
  const marbleMat = twoTone(new THREE.MeshLambertMaterial({ color: "#f2ece1" }));
  const trimMat = twoTone(new THREE.MeshLambertMaterial({ color: "#d5cbb8" }));
  const archDarkMat = twoTone(new THREE.MeshLambertMaterial({ color: "#4a433d" }));
  const roofMat = twoTone(new THREE.MeshLambertMaterial({ color: "#b85a3a" }));
  const cypressMat = twoTone(new THREE.MeshLambertMaterial({ color: "#2d5a34" }));

  // Travertine piazza floor covering the generic grass around the stage
  const floor = new THREE.Mesh(new THREE.BoxGeometry(30, 0.04, 26), plazaMat);
  floor.position.set(0, 0.02, 0);
  floor.receiveShadow = true;
  stageGroup.add(floor);

  // Renaissance Cathedral Colonnade backdrop (replaces modern German town behind Pisa)
  const backWall = new THREE.Mesh(new THREE.BoxGeometry(22, 6.2, 1.2), marbleMat);
  backWall.position.set(0, 3.1, -6.8);
  const backRoof = new THREE.Mesh(new THREE.BoxGeometry(22.6, 0.5, 1.8), roofMat);
  backRoof.position.set(0, 6.4, -6.8);
  stageGroup.add(backWall, backRoof);

  for (let i = -4; i <= 4; i++) {
    const px = i * 2.3;
    const pilaster = new THREE.Mesh(new THREE.BoxGeometry(0.42, 5.6, 0.45), trimMat);
    pilaster.position.set(px, 2.8, -6.1);
    const alcove = new THREE.Mesh(new THREE.BoxGeometry(1.35, 3.4, 0.25), archDarkMat);
    alcove.position.set(px + 1.15, 2.2, -6.22);
    stageGroup.add(pilaster);
    if (i < 4) stageGroup.add(alcove);
  }

  // Flanking Tuscan cypress trees
  for (const [tx, tz, h] of [
    [-6.2, -4.6, 4.4],
    [-4.8, -5.2, 5.1],
    [5.8, -4.9, 4.8],
    [7.1, -4.2, 4.1],
  ]) {
    const trunk = new THREE.Mesh(new THREE.CylinderGeometry(0.12, 0.16, 1.1, 8), mats.wood);
    trunk.position.set(tx, 0.55, tz);
    const crown = new THREE.Mesh(new THREE.ConeGeometry(0.65, h, 10), cypressMat);
    crown.position.set(tx, 1.0 + h * 0.5, tz);
    stageGroup.add(trunk, crown);
  }

  // Hero 6-tier Leaning Tower of Pisa at (-1.35, 0, -1.55), tilted -0.075 rad
  towerGroup.position.set(-1.35, 0, -1.55);
  towerGroup.rotation.z = -0.075;
  const plinth = new THREE.Mesh(new THREE.CylinderGeometry(0.95, 1.02, 0.55, 24), trimMat);
  plinth.position.y = 0.28;
  towerGroup.add(plinth);

  for (let tier = 0; tier < 6; tier++) {
    const r = 0.78 - tier * 0.025;
    const yBase = 0.55 + tier * 0.68;
    const drum = new THREE.Mesh(new THREE.CylinderGeometry(r, r + 0.015, 0.62, 24), marbleMat);
    drum.position.y = yBase + 0.31;
    const cornice = new THREE.Mesh(new THREE.CylinderGeometry(r + 0.07, r + 0.07, 0.08, 24), trimMat);
    cornice.position.y = yBase + 0.64;
    towerGroup.add(drum, cornice);

    // Ring of dark colonnade arches around each tier
    for (let a = 0; a < 8; a++) {
      const ang = (a / 8) * Math.PI * 2;
      const win = new THREE.Mesh(new THREE.BoxGeometry(0.14, 0.34, 0.08), archDarkMat);
      win.position.set(Math.sin(ang) * (r + 0.01), yBase + 0.32, Math.cos(ang) * (r + 0.01));
      win.rotation.y = ang;
      towerGroup.add(win);
    }
  }

  // Top belfry tier + stone balcony railing at y = 4.65
  const belfry = new THREE.Mesh(new THREE.CylinderGeometry(0.56, 0.6, 0.58, 20), marbleMat);
  belfry.position.y = 4.92;
  const railRing = new THREE.Mesh(new THREE.TorusGeometry(0.72, 0.05, 8, 24), mats.stone);
  railRing.rotation.x = Math.PI / 2;
  railRing.position.y = 4.65;
  towerGroup.add(belfry, railRing);
  stageGroup.add(towerGroup);

  return towerGroup;
}

export function buildGalileoMoonDome(root: THREE.Group, mats: GalileoSceneMats): {
  moonGroup: THREE.Group;
  moonEarth: THREE.Mesh;
  moonHammer: THREE.Group;
  moonFeather: THREE.Group;
} {
  const moonGroup = new THREE.Group();
  moonGroup.position.set(0, MOON_Y, 0);

  // Full 360-deg starry space sky dome (completely isolates Moon shot from Earth ground & town)
  const skyDome = new THREE.Mesh(
    new THREE.SphereGeometry(120, 32, 20),
    new THREE.MeshBasicMaterial({ map: starfieldTex(), side: THREE.BackSide, fog: false })
  );
  skyDome.layers.set(NOINK);
  moonGroup.add(skyDome);

  // Glowing planet Earth hanging in the lunar sky
  const moonEarth = new THREE.Mesh(
    new THREE.SphereGeometry(3.4, 24, 18),
    new THREE.MeshBasicMaterial({ map: earthTex(), fog: false })
  );
  moonEarth.position.set(-4.2, 8.5, 28);
  moonEarth.layers.set(NOINK);
  moonGroup.add(moonEarth);

  // Cratered lunar regolith surface + raised crater rims + moon rocks
  const regolithMat = twoTone(new THREE.MeshLambertMaterial({ color: "#9ba0aa" }));
  const craterMat = twoTone(new THREE.MeshLambertMaterial({ color: "#7f8591" }));
  const rockMat = twoTone(new THREE.MeshLambertMaterial({ color: "#686e7a" }));
  const moonFloor = new THREE.Mesh(new THREE.CylinderGeometry(42, 42, 0.4, 40), regolithMat);
  moonFloor.position.set(0, -0.2, 0);
  moonFloor.receiveShadow = true;
  moonGroup.add(moonFloor);

  for (const [cx, cz, cr] of [
    [-1.4, -0.8, 0.52],
    [1.6, 0.4, 0.42],
    [0.2, 1.9, 0.65],
    [-3.2, 3.8, 0.9],
    [3.8, 4.5, 1.1],
    [-2.5, -3.2, 0.75],
    [2.9, -2.6, 0.6],
  ]) {
    const rim = new THREE.Mesh(new THREE.TorusGeometry(cr, 0.08, 8, 18), craterMat);
    rim.rotation.x = Math.PI / 2;
    rim.position.set(cx, 0.03, cz);
    moonGroup.add(rim);
  }
  for (const [rx, rz, rs] of [
    [-2.2, 1.2, 0.24],
    [2.1, -1.1, 0.3],
    [4.4, 2.2, 0.42],
    [-4.1, 2.6, 0.36],
  ]) {
    const rock = new THREE.Mesh(new THREE.DodecahedronGeometry(rs, 0), rockMat);
    rock.position.set(rx, rs * 0.5, rz);
    rock.rotation.set(rx, rz, 0.4);
    moonGroup.add(rock);
  }

  // Hammer + White Feather for lunar drop test
  const mSilver = twoTone(new THREE.MeshPhongMaterial({ color: "#cfd6e0", specular: "#ffffff", shininess: 85 }), 0.18);
  const moonHammer = new THREE.Group();
  const hStick = new THREE.Mesh(new THREE.CylinderGeometry(0.03, 0.03, 0.48, 8), mats.wood);
  const hHead = new THREE.Mesh(new THREE.BoxGeometry(0.26, 0.11, 0.11), mSilver);
  hHead.position.y = 0.22;
  moonHammer.add(hStick, hHead);

  const moonFeather = new THREE.Group();
  const mfShaft = new THREE.Mesh(new THREE.CylinderGeometry(0.015, 0.02, 0.42, 8), mats.paper);
  const mfPlume = new THREE.Mesh(new THREE.BoxGeometry(0.16, 0.34, 0.03), mats.paper);
  moonFeather.add(mfShaft, mfPlume);

  moonGroup.add(moonHammer, moonFeather);
  root.add(moonGroup);

  return { moonGroup, moonEarth, moonHammer, moonFeather };
}
