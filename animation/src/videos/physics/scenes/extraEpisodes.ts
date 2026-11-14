// Modular 3D Scenes + Choreography for PascalShort, DopplerShort, and CurieShort.
import * as THREE from "three";
import { NOINK } from "../../bridge/ink";
import { twoTone } from "../../bridge/shade";
import {
  Pen,
  INK,
  bodyFront,
  bodySide,
  townsfolk,
  KID,
  PARENT,
  fxBurst,
  fxSplash,
  fxStars,
  Outfit,
  Expr,
} from "../../bridge/toon";
import { V3, FPS, clamp01 } from "../../bridge/story";
import { enrichExtraEnvironment } from "./extraEnvironments";

export type ExtraEpId = "pascal" | "doppler" | "curie";

export type ExtraPlace = {
  key: string;
  draw: (p: Pen) => void;
  x: number;
  y: number;
  z: number;
  scale?: number;
  mirror?: boolean;
};

export type ExtraFx = {
  key: string;
  cw: number;
  ch: number;
  draw: (p: Pen) => void;
  x: number;
  y: number;
  z: number;
  w: number;
  h: number;
};

const PASCAL_OUTFIT: Outfit = {
  jacket: "#3a4b6e",
  pants: "#232936",
  boots: INK,
  hat: "hair",
  hair: "#4c3627",
  buttons: "#e2b857",
};
const DOPPLER_OUTFIT: Outfit = {
  jacket: "#5b2d38",
  pants: "#27252b",
  boots: INK,
  hat: "tophat",
  buttons: "#d9c27a",
};
const MARIE_OUTFIT: Outfit = {
  jacket: "#252933",
  pants: "#1d2028",
  boots: INK,
  hat: "hair",
  hair: "#6a4c38",
  dress: "#2b303d",
};
const PIERRE_OUTFIT: Outfit = {
  jacket: "#3b3530",
  pants: "#24211e",
  boots: INK,
  hat: "hair",
  hair: "#4a3b2e",
  moustache: "#4a3b2e",
};

export interface ExtraRig {
  // Pascal
  barrelBody: THREE.Mesh;
  hoopTop: THREE.Mesh;
  hoopBot: THREE.Mesh;
  waterColumn: THREE.Mesh;
  carLiftPlatform: THREE.Group;
  smallPiston: THREE.Mesh;
  // Doppler
  trainGroup: THREE.Group;
  frontWaves: THREE.Mesh[];
  backWaves: THREE.Mesh[];
  galaxyStar: THREE.Mesh;
  redshiftWaves: THREE.Mesh[];
  // Curie
  shedWall: THREE.Mesh;
  cauldronSteam: THREE.Mesh[];
  radiumVials: THREE.Mesh[];
  atomParticles: THREE.Mesh[];
  watchDial: THREE.Mesh;
}

export function buildExtraShots(ep: ExtraEpId, stage: V3, park: V3) {
  const [sx, sy, sz] = stage;
  const [px, py, pz] = park;
  const B = [0, 140, 280, 420, 560, 700, 840, 980, 1120, 1260, 1400, 1540, 1680, 1820, 1960, 2100];
  const S = (id: number, light: "day" | "golden", cInf: number, pos0: V3, look0: V3, pos1: V3, look1: V3, extra: { fov?: number; kickAt?: number } = {}) => ({
    id, a: B[id - 1], b: B[id], light, cInf, pos0, look0, pos1, look1, fov: extra.fov ?? 44, kickAt: extra.kickAt,
  });

  if (ep === "pascal") {
    return [
      S(1, "day", 7, [sx + 0.5, sy + 1.8, sz + 7.2], [sx, sy + 1.5, sz], [sx + 0.2, sy + 1.65, sz + 6.0], [sx, sy + 1.5, sz]),
      S(2, "day", 8, [sx - 0.7, sy + 1.4, sz + 5.2], [sx - 0.4, sy + 1.1, sz - 0.3], [sx - 0.4, sy + 1.35, sz + 4.4], [sx - 0.4, sy + 1.05, sz - 0.3]),
      S(3, "day", 8, [sx + 1.3, sy + 1.6, sz + 6.2], [sx + 0.5, sy + 1.2, sz], [sx + 0.8, sy + 1.5, sz + 5.3], [sx + 0.5, sy + 1.2, sz]),
      S(4, "day", 7, [sx + 0.2, sy + 2.4, sz + 6.8], [sx - 0.3, sy + 2.2, sz - 0.5], [sx + 0.1, sy + 3.2, sz + 6.4], [sx - 0.3, sy + 2.8, sz - 0.5]),
      S(5, "day", 8, [sx + 0.6, sy + 4.0, sz + 5.2], [sx - 0.6, sy + 4.1, sz - 0.6], [sx + 0.3, sy + 4.4, sz + 4.4], [sx - 0.6, sy + 4.3, sz - 0.6]),
      S(6, "day", 8, [sx + 1.5, sy + 1.5, sz + 5.8], [sx + 0.4, sy + 1.3, sz], [sx + 1.1, sy + 1.8, sz + 5.4], [sx + 0.2, sy + 1.8, sz]),
      S(7, "day", 9, [sx + 0.2, sy + 4.6, sz + 3.6], [sx - 0.65, sy + 4.4, sz - 0.5], [sx - 0.1, sy + 4.5, sz + 2.9], [sx - 0.65, sy + 4.35, sz - 0.5]),
      S(8, "day", 8, [sx - 0.2, sy + 3.2, sz + 5.6], [sx - 0.4, sy + 2.1, sz - 0.4], [sx - 0.3, sy + 1.6, sz + 4.8], [sx - 0.4, sy + 1.1, sz - 0.4]),
      S(9, "day", 7, [sx + 0.4, sy + 1.6, sz + 5.6], [sx - 0.2, sy + 1.1, sz - 0.2], [sx + 0.8, sy + 1.8, sz + 6.4], [sx - 0.1, sy + 1.1, sz - 0.2], { kickAt: 1140 }),
      S(10, "day", 8, [sx + 1.4, sy + 1.6, sz + 6.2], [sx + 0.3, sy + 1.2, sz + 0.2], [sx + 2.0, sy + 1.5, sz + 5.4], [sx + 0.5, sy + 1.2, sz + 0.2]),
      S(11, "golden", 7, [px - 0.6, py + 1.7, pz - 6.0], [px, py + 1.25, pz], [px - 0.2, py + 1.55, pz - 5.0], [px, py + 1.2, pz]),
      S(12, "golden", 8, [px + 0.3, py + 1.6, pz - 5.6], [px, py + 1.2, pz], [px + 0.1, py + 1.45, pz - 4.7], [px, py + 1.2, pz]),
      S(13, "golden", 8, [px - 0.4, py + 1.8, pz - 5.8], [px, py + 1.35, pz], [px, py + 1.6, pz - 4.8], [px, py + 1.3, pz]),
      S(14, "golden", 8, [px + 0.5, py + 1.9, pz - 6.0], [px + 0.1, py + 1.4, pz], [px + 0.2, py + 1.75, pz - 5.0], [px + 0.1, py + 1.4, pz]),
      S(15, "day", 6, [sx - 0.3, sy + 1.8, sz + 6.4], [sx, sy + 1.3, sz], [sx + 0.4, sy + 2.4, sz + 8.4], [sx, sy + 1.4, sz], { fov: 46 }),
    ];
  }

  if (ep === "doppler") {
    return [
      S(1, "day", 7, [sx + 0.4, sy + 1.8, sz + 7.4], [sx, sy + 1.35, sz], [sx - 0.2, sy + 1.65, sz + 6.2], [sx, sy + 1.35, sz]),
      S(2, "day", 8, [sx + 1.2, sy + 1.6, sz + 5.8], [sx + 0.2, sy + 1.25, sz], [sx + 0.7, sy + 1.5, sz + 4.9], [sx + 0.2, sy + 1.25, sz]),
      S(3, "day", 8, [sx + 1.5, sy + 1.5, sz + 5.6], [sx + 0.6, sy + 1.2, sz + 0.3], [sx + 1.0, sy + 1.4, sz + 4.7], [sx + 0.6, sy + 1.2, sz + 0.3]),
      S(4, "day", 7, [sx - 1.2, sy + 1.7, sz + 6.4], [sx - 0.5, sy + 1.3, sz - 0.4], [sx + 0.2, sy + 1.6, sz + 5.8], [sx, sy + 1.3, sz - 0.4]),
      S(5, "day", 8, [sx + 0.5, sy + 1.6, sz + 5.8], [sx - 0.2, sy + 1.3, sz - 0.3], [sx + 0.1, sy + 1.5, sz + 5.0], [sx, sy + 1.3, sz - 0.3]),
      S(6, "day", 7, [sx + 0.8, sy + 1.7, sz + 6.0], [sx + 0.4, sy + 1.3, sz - 0.3], [sx + 1.4, sy + 1.7, sz + 5.6], [sx + 0.8, sy + 1.3, sz - 0.3], { kickAt: 715 }),
      S(7, "day", 8, [sx + 1.4, sy + 1.5, sz + 5.4], [sx + 0.7, sy + 1.25, sz + 0.3], [sx + 1.0, sy + 1.45, sz + 4.6], [sx + 0.7, sy + 1.25, sz + 0.3]),
      S(8, "day", 8, [sx - 0.4, sy + 1.8, sz + 6.2], [sx, sy + 1.35, sz - 0.3], [sx, sy + 1.65, sz + 5.2], [sx, sy + 1.35, sz - 0.3]),
      S(9, "day", 8, [sx + 0.6, sy + 1.8, sz + 6.2], [sx + 0.2, sy + 1.35, sz - 0.3], [sx + 0.2, sy + 1.65, sz + 5.2], [sx + 0.2, sy + 1.35, sz - 0.3]),
      S(10, "day", 7, [sx + 0.2, sy + 1.7, sz + 6.6], [sx + 0.2, sy + 1.3, sz], [sx - 0.3, sy + 1.6, sz + 5.6], [sx + 0.2, sy + 1.3, sz]),
      S(11, "golden", 7, [px - 0.6, py + 1.7, pz - 6.0], [px, py + 1.3, pz], [px - 0.2, py + 1.55, pz - 5.0], [px, py + 1.3, pz]),
      S(12, "golden", 8, [px + 0.4, py + 1.6, pz - 5.6], [px, py + 1.25, pz], [px, py + 1.45, pz - 4.8], [px, py + 1.25, pz]),
      S(13, "golden", 8, [px - 0.4, py + 1.8, pz - 5.8], [px, py + 1.4, pz], [px + 0.1, py + 1.6, pz - 4.9], [px, py + 1.4, pz]),
      S(14, "golden", 8, [px + 0.5, py + 1.8, pz - 5.8], [px, py + 1.4, pz], [px + 0.2, py + 1.65, pz - 4.8], [px, py + 1.4, pz]),
      S(15, "day", 6, [sx - 0.4, sy + 1.8, sz + 6.6], [sx, sy + 1.3, sz], [sx + 0.5, sy + 2.4, sz + 8.6], [sx, sy + 1.4, sz], { fov: 46 }),
    ];
  }

  // curie
  return [
    S(1, "day", 8, [sx + 0.5, sy + 1.65, sz + 6.0], [sx, sy + 1.25, sz], [sx + 0.1, sy + 1.5, sz + 5.0], [sx, sy + 1.25, sz]),
    S(2, "day", 8, [sx - 0.7, sy + 1.6, sz + 5.6], [sx - 0.2, sy + 1.15, sz - 0.2], [sx - 0.3, sy + 1.45, sz + 4.7], [sx - 0.2, sy + 1.15, sz - 0.2]),
    S(3, "day", 9, [sx - 0.4, sy + 1.5, sz + 4.9], [sx - 0.3, sy + 1.1, sz - 0.2], [sx, sy + 1.4, sz + 4.2], [sx - 0.3, sy + 1.1, sz - 0.2]),
    S(4, "day", 8, [sx + 1.1, sy + 1.6, sz + 5.8], [sx + 0.2, sy + 1.25, sz], [sx + 0.7, sy + 1.5, sz + 5.0], [sx + 0.2, sy + 1.25, sz]),
    S(5, "day", 9, [sx + 0.2, sy + 1.45, sz + 4.8], [sx, sy + 1.2, sz - 0.1], [sx, sy + 1.38, sz + 4.0], [sx, sy + 1.2, sz - 0.1]),
    S(6, "day", 9, [sx - 0.3, sy + 1.5, sz + 4.8], [sx - 0.1, sy + 1.2, sz - 0.2], [sx + 0.1, sy + 1.4, sz + 4.0], [sx - 0.1, sy + 1.2, sz - 0.2]),
    S(7, "day", 9, [sx + 0.3, sy + 1.5, sz + 4.6], [sx, sy + 1.2, sz - 0.2], [sx - 0.1, sy + 1.4, sz + 3.9], [sx, sy + 1.2, sz - 0.2]),
    S(8, "day", 9, [sx - 0.2, sy + 1.55, sz + 4.8], [sx, sy + 1.25, sz - 0.1], [sx + 0.2, sy + 1.45, sz + 4.1], [sx, sy + 1.25, sz - 0.1]),
    S(9, "day", 8, [sx + 0.4, sy + 1.6, sz + 5.4], [sx, sy + 1.25, sz], [sx, sy + 1.5, sz + 4.6], [sx, sy + 1.25, sz]),
    S(10, "day", 8, [sx + 0.9, sy + 1.65, sz + 5.8], [sx + 0.2, sy + 1.25, sz], [sx + 0.4, sy + 1.5, sz + 4.9], [sx + 0.2, sy + 1.25, sz]),
    S(11, "golden", 7, [px - 0.6, py + 1.7, pz - 6.0], [px, py + 1.3, pz], [px - 0.2, py + 1.55, pz - 5.0], [px, py + 1.3, pz]),
    S(12, "golden", 8, [px + 0.3, py + 1.6, pz - 5.4], [px, py + 1.3, pz], [px, py + 1.45, pz - 4.6], [px, py + 1.3, pz]),
    S(13, "golden", 8, [px - 0.4, py + 1.65, pz - 5.4], [px, py + 1.25, pz], [px, py + 1.5, pz - 4.5], [px, py + 1.25, pz]),
    S(14, "golden", 8, [px + 0.4, py + 1.7, pz - 5.6], [px, py + 1.3, pz], [px + 0.1, py + 1.55, pz - 4.7], [px, py + 1.3, pz]),
    S(15, "day", 6, [sx - 0.4, sy + 1.75, sz + 6.0], [sx, sy + 1.25, sz], [sx + 0.4, sy + 2.3, sz + 8.0], [sx, sy + 1.35, sz], { fov: 46 }),
  ];
}

export function buildExtraProps(
  ep: ExtraEpId,
  stageGroup: THREE.Group,
  analogyGroup: THREE.Group,
  mats: { wood: THREE.Material; stone: THREE.Material; iron: THREE.Material; copper: THREE.Material; brass: THREE.Material; glass: THREE.Material; red: THREE.Material; paper: THREE.Material }
): ExtraRig {
  const mk = () => new THREE.Mesh();
  const mg = () => new THREE.Group();
  const mBlue = twoTone(new THREE.MeshLambertMaterial({ color: "#3b76c4" }));
  const mWater = twoTone(new THREE.MeshPhongMaterial({ color: "#55b8db", specular: "#ffffff", shininess: 90, transparent: true, opacity: 0.78 }), 0.15);
  const rig: ExtraRig = {
    barrelBody: mk(), hoopTop: mk(), hoopBot: mk(), waterColumn: mk(), carLiftPlatform: mg(), smallPiston: mk(),
    trainGroup: mg(), frontWaves: [], backWaves: [], galaxyStar: mk(), redshiftWaves: [],
    shedWall: mk(), cauldronSteam: [], radiumVials: [], atomParticles: [], watchDial: mk(),
  };

  if (ep === "pascal") {
    // 1646 Courtyard + Giant Oak Barrel + 4.8m thin pipe + ladder
    const court = new THREE.Mesh(new THREE.BoxGeometry(24, 0.04, 20), twoTone(new THREE.MeshLambertMaterial({ color: "#cfc6b4" })));
    court.position.set(0, 0.02, 0);
    rig.barrelBody = new THREE.Mesh(new THREE.CylinderGeometry(0.68, 0.68, 1.3, 18), mats.wood);
    rig.barrelBody.position.set(-0.65, 0.68, -0.5);
    rig.hoopTop = new THREE.Mesh(new THREE.TorusGeometry(0.7, 0.05, 8, 20), mats.iron);
    rig.hoopTop.rotation.x = Math.PI / 2;
    rig.hoopTop.position.set(-0.65, 1.15, -0.5);
    rig.hoopBot = new THREE.Mesh(new THREE.TorusGeometry(0.7, 0.05, 8, 20), mats.iron);
    rig.hoopBot.rotation.x = Math.PI / 2;
    rig.hoopBot.position.set(-0.65, 0.35, -0.5);
    const pipe = new THREE.Mesh(new THREE.CylinderGeometry(0.06, 0.06, 3.6, 10), mats.glass);
    pipe.position.set(-0.65, 3.1, -0.5);
    rig.waterColumn = new THREE.Mesh(new THREE.CylinderGeometry(0.045, 0.045, 3.5, 10), mWater);
    rig.waterColumn.position.set(-0.65, 3.05, -0.5);
    const ladderL = new THREE.Mesh(new THREE.BoxGeometry(0.08, 4.6, 0.08), mats.wood);
    ladderL.position.set(-1.35, 2.3, -0.7);
    const ladderR = new THREE.Mesh(new THREE.BoxGeometry(0.08, 4.6, 0.08), mats.wood);
    ladderR.position.set(-0.95, 2.3, -0.7);
    stageGroup.add(court, rig.barrelBody, rig.hoopTop, rig.hoopBot, pipe, rig.waterColumn, ladderL, ladderR);

    // Park hydraulic car lift
    const baseTank = new THREE.Mesh(new THREE.BoxGeometry(2.6, 0.28, 1.1), mats.iron);
    baseTank.position.set(0, 0.14, 0);
    rig.smallPiston = new THREE.Mesh(new THREE.CylinderGeometry(0.16, 0.16, 1.2, 12), mats.brass);
    rig.smallPiston.position.set(-0.85, 0.8, 0);
    const bigCyl = new THREE.Mesh(new THREE.CylinderGeometry(0.45, 0.45, 0.9, 14), mats.iron);
    bigCyl.position.set(0.65, 0.55, 0);
    const plat = new THREE.Mesh(new THREE.BoxGeometry(1.5, 0.14, 1.0), mats.iron);
    const carBody = new THREE.Mesh(new THREE.BoxGeometry(1.25, 0.48, 0.72), mats.red);
    carBody.position.y = 0.31;
    const carCabin = new THREE.Mesh(new THREE.BoxGeometry(0.7, 0.32, 0.64), mBlue);
    carCabin.position.y = 0.68;
    rig.carLiftPlatform.add(plat, carBody, carCabin);
    rig.carLiftPlatform.position.set(0.65, 1.05, 0);
    analogyGroup.add(baseTank, rig.smallPiston, bigCyl, rig.carLiftPlatform);
  }

  if (ep === "doppler") {
    // 1845 Railway Tracks + Platform + Steam Train Flatcar + Sound Wave Torus Rings
    const ballast = new THREE.Mesh(new THREE.BoxGeometry(26, 0.08, 2.2), mats.stone);
    ballast.position.set(0, 0.04, -0.5);
    const rail1 = new THREE.Mesh(new THREE.BoxGeometry(26, 0.08, 0.08), mats.iron);
    rail1.position.set(0, 0.12, -0.9);
    const rail2 = new THREE.Mesh(new THREE.BoxGeometry(26, 0.08, 0.08), mats.iron);
    rail2.position.set(0, 0.12, -0.1);
    const plat = new THREE.Mesh(new THREE.BoxGeometry(9.5, 0.25, 2.4), mats.wood);
    plat.position.set(0.5, 0.12, 1.2);
    stageGroup.add(ballast, rail1, rail2, plat);

    const loco = new THREE.Mesh(new THREE.BoxGeometry(1.9, 0.95, 1.05), mats.iron);
    loco.position.set(0.9, 0.65, 0);
    const stack = new THREE.Mesh(new THREE.CylinderGeometry(0.14, 0.18, 0.65, 10), mats.copper);
    stack.position.set(1.45, 1.35, 0);
    const flatcar = new THREE.Mesh(new THREE.BoxGeometry(2.3, 0.25, 1.1), mats.red);
    flatcar.position.set(-1.35, 0.35, 0);
    rig.trainGroup.add(loco, stack, flatcar);
    rig.trainGroup.position.set(0, 0.1, -0.5);
    stageGroup.add(rig.trainGroup);

    const waveBlue = new THREE.MeshBasicMaterial({ color: new THREE.Color(0.8, 2.2, 3.6), transparent: true, opacity: 0.75 });
    const waveRed = new THREE.MeshBasicMaterial({ color: new THREE.Color(3.6, 0.9, 0.9), transparent: true, opacity: 0.75 });
    for (let i = 0; i < 4; i++) {
      const wf = new THREE.Mesh(new THREE.TorusGeometry(0.45 + i * 0.18, 0.035, 8, 20), waveBlue);
      wf.rotation.y = Math.PI / 2;
      wf.layers.set(NOINK);
      rig.frontWaves.push(wf);
      const wb = new THREE.Mesh(new THREE.TorusGeometry(0.45 + i * 0.22, 0.035, 8, 20), waveRed);
      wb.rotation.y = Math.PI / 2;
      wb.layers.set(NOINK);
      rig.backWaves.push(wb);
      stageGroup.add(wf, wb);
    }

    // Park analogy: receding star + redshifted light wave rings
    rig.galaxyStar = new THREE.Mesh(new THREE.SphereGeometry(0.36, 16, 12), new THREE.MeshBasicMaterial({ color: new THREE.Color(3.4, 2.8, 1.2) }));
    rig.galaxyStar.layers.set(NOINK);
    analogyGroup.add(rig.galaxyStar);
    for (let i = 0; i < 4; i++) {
      const rw = new THREE.Mesh(new THREE.TorusGeometry(0.35 + i * 0.25, 0.035, 8, 20), waveRed);
      rw.layers.set(NOINK);
      rig.redshiftWaves.push(rw);
      analogyGroup.add(rw);
    }
  }

  if (ep === "curie") {
    // 1898 Dark Wooden Shed + Iron Cauldron + Electric-Blue Glowing Radium Vials
    const darkWood = twoTone(new THREE.MeshLambertMaterial({ color: "#1c1917" }));
    rig.shedWall = new THREE.Mesh(new THREE.BoxGeometry(8.5, 4.6, 0.25), darkWood);
    rig.shedWall.position.set(0, 2.3, -1.7);
    const bench = new THREE.Mesh(new THREE.BoxGeometry(2.2, 0.85, 0.8), mats.wood);
    bench.position.set(0.85, 0.42, -0.35);
    const cauldron = new THREE.Mesh(new THREE.CylinderGeometry(0.65, 0.5, 0.78, 16), mats.iron);
    cauldron.position.set(-0.7, 0.39, -0.35);
    stageGroup.add(rig.shedWall, bench, cauldron);

    const glowMat = new THREE.MeshBasicMaterial({ color: new THREE.Color(0.8, 2.6, 4.8) });
    for (let i = 0; i < 3; i++) {
      const vial = new THREE.Mesh(new THREE.CylinderGeometry(0.08, 0.08, 0.32, 10), glowMat);
      vial.position.set(0.45 + i * 0.38, 1.02, -0.35);
      vial.layers.set(NOINK);
      rig.radiumVials.push(vial);
      stageGroup.add(vial);
    }
    const steamMat = new THREE.MeshBasicMaterial({ color: new THREE.Color(1.2, 1.3, 1.5), transparent: true, opacity: 0.55 });
    for (let i = 0; i < 3; i++) {
      const st = new THREE.Mesh(new THREE.SphereGeometry(0.2, 10, 8), steamMat);
      st.layers.set(NOINK);
      rig.cauldronSteam.push(st);
      stageGroup.add(st);
    }

    // Park analogy: glowing watch dial + atom nucleus popping glowing particles
    const nuc = new THREE.Mesh(new THREE.SphereGeometry(0.32, 16, 12), glowMat);
    nuc.position.set(0, 1.25, 0);
    nuc.layers.set(NOINK);
    rig.watchDial = new THREE.Mesh(new THREE.CylinderGeometry(0.52, 0.52, 0.08, 20), glowMat);
    rig.watchDial.rotation.x = Math.PI / 2;
    rig.watchDial.position.set(0, 1.25, -0.3);
    rig.watchDial.layers.set(NOINK);
    analogyGroup.add(nuc, rig.watchDial);
    for (let i = 0; i < 5; i++) {
      const pt = new THREE.Mesh(new THREE.SphereGeometry(0.08, 8, 8), glowMat);
      pt.layers.set(NOINK);
      rig.atomParticles.push(pt);
      analogyGroup.add(pt);
    }
  }

  enrichExtraEnvironment(ep, stageGroup, mats);
  return rig;
}

export function updateExtraEpisode(
  ep: ExtraEpId,
  f: number,
  shot: { id: number; a: number; b: number },
  rig: ExtraRig,
  stageCenter: V3,
  parkCenter: V3,
  places: ExtraPlace[],
  fxList: ExtraFx[]
) {
  const [SX, SY, SZ] = stageCenter;
  const [PX, PY, PZ] = parkCenter;
  const t = f / FPS;
  const pose = Math.floor(t * 8) % 8;
  const blink = (s: number) => ((f + s * 19) % 58) < 4;

  if (ep === "pascal") {
    const burst = shot.id >= 9 && shot.id <= 10;
    const fillU = shot.id === 7 || shot.id === 8 ? clamp01((f - shot.a) / 90) : burst ? 1 : 0;
    rig.waterColumn.scale.y = Math.max(0.05, fillU);
    rig.hoopTop.position.x = burst ? -0.95 : -0.65;
    rig.hoopBot.position.x = burst ? -0.35 : -0.65;
    rig.barrelBody.scale.setScalar(burst ? 1.08 : 1.0 + fillU * 0.05);

    const climbU = shot.id === 5 ? clamp01((f - shot.a) / 60) : shot.id >= 6 && shot.id <= 8 ? 1 : 0;
    places.push({
      key: `ps|${climbU > 0.5 ? "hi" : "lo"}|${pose}`,
      draw: (p) => bodyFront(p, PASCAL_OUTFIT, { mode: "stand", expr: burst ? "grin" : "smile", blink: blink(1), wave: shot.id === 7 ? 0.85 : 0.4 }),
      x: SX - 1.15,
      y: SY + climbU * 3.35,
      z: SZ - 0.55,
    });
    const runAway = shot.id === 9 || shot.id === 10 ? clamp01((f - shot.a) / 70) : 0;
    for (let i = 0; i < 3; i++) {
      places.push({
        key: `psC|${i}|${runAway > 0 ? "r" : "s"}|${pose}`,
        draw: (p) =>
          runAway > 0
            ? bodySide(p, townsfolk(i), { mode: "march", expr: "shock", phase: (t * 3.1 + i * 0.25) % 1 })
            : bodyFront(p, townsfolk(i), { mode: "stand", expr: shot.id === 3 ? "grin" : "smile", wave: 0.4 }),
        x: SX + 0.5 + i * 0.55 + runAway * 2.5,
        y: SY,
        z: SZ + 0.45 + (i % 2) * 0.2,
      });
    }
    if (shot.id === 9 && f >= 1140 && f < 1190) {
      fxList.push({ key: `psSpl|${f % 3}`, cw: 240, ch: 240, draw: (p) => fxSplash(p, 0.5), x: SX - 0.65, y: SY + 0.9, z: SZ - 0.3, w: 1.8, h: 1.5 });
    }
    const liftU = shot.id >= 11 && shot.id <= 14 ? 0.5 + 0.45 * Math.sin(t * 2.2) : 0.2;
    rig.smallPiston.position.y = 0.6 + (1 - liftU) * 0.4;
    rig.carLiftPlatform.position.y = 0.75 + liftU * 0.75;
    if (shot.id >= 11 && shot.id <= 14) {
      places.push({ key: `psPk|${pose}`, draw: (p) => bodyFront(p, KID, { mode: "stand", expr: "grin", wave: 0.6 }), x: PX - 1.55, y: PY, z: PZ + 0.15, scale: 0.84 });
    }
    return;
  }

  if (ep === "doppler") {
    const driveU = shot.id >= 4 && shot.id <= 7 ? ((f - 420) / 560) : 0.5;
    const trainX = (driveU - 0.5) * 10.5;
    rig.trainGroup.position.x = shot.id >= 4 && shot.id <= 7 ? trainX : 0;
    rig.frontWaves.forEach((w, i) => {
      const p = ((t * 1.8 + i * 0.25) % 1);
      w.visible = shot.id >= 4 && shot.id <= 9;
      w.position.set(rig.trainGroup.position.x + 1.5 + p * 1.1, 1.0, -0.5);
    });
    rig.backWaves.forEach((w, i) => {
      const p = ((t * 1.2 + i * 0.25) % 1);
      w.visible = shot.id >= 4 && shot.id <= 9;
      w.position.set(rig.trainGroup.position.x - 1.6 - p * 2.4, 1.0, -0.5);
    });
    places.push({
      key: `dp|${pose}`,
      draw: (p) => bodyFront(p, DOPPLER_OUTFIT, { mode: "stand", expr: shot.id >= 10 ? "grin" : "smile", blink: blink(1), wave: 0.55 }),
      x: SX - 0.65,
      y: SY,
      z: SZ + 0.75,
    });
    for (let i = 0; i < 3; i++) {
      places.push({
        key: `dpS|${i}|${shot.id}|${pose}`,
        draw: (p) => bodyFront(p, townsfolk(i + 1), { mode: "stand", expr: shot.id >= 6 && shot.id <= 7 ? "shock" : "smile" }),
        x: SX + 0.45 + i * 0.55,
        y: SY,
        z: SZ + 0.8 + (i % 2) * 0.2,
      });
    }
    rig.galaxyStar.position.set((shot.id === 13 || shot.id === 14 ? (t * 0.6) % 1.4 - 0.4 : 0), 1.35, 0);
    rig.redshiftWaves.forEach((rw, i) => {
      rw.visible = shot.id >= 11 && shot.id <= 14;
      const p = ((t * 1.5 + i * 0.25) % 1);
      rw.position.set(rig.galaxyStar.position.x - p * 1.8, 1.35, 0);
    });
    if (shot.id >= 11 && shot.id <= 14) {
      places.push({ key: `dpPk|${pose}`, draw: (p) => bodyFront(p, PARENT, { mode: "stand", expr: "grin", wave: 0.5 }), x: PX - 1.5, y: PY, z: PZ + 0.15 });
    }
    return;
  }

  // curie
  const glowOn = shot.id >= 5;
  rig.radiumVials.forEach((v) => { v.visible = glowOn; });
  rig.cauldronSteam.forEach((st, i) => {
    st.visible = shot.id >= 2 && shot.id <= 4;
    const p = ((t * 1.2 + i * 0.33) % 1);
    st.position.set(-0.7 + Math.sin(t * 2 + i) * 0.15, 0.9 + p * 1.3, -0.35);
    st.scale.setScalar(0.7 + p * 0.9);
  });
  if (glowOn && f % 4 < 2) {
    fxList.push({ key: `cuGlow|${f % 3}`, cw: 220, ch: 220, draw: (p) => fxStars(p, (f % 10) / 10), x: SX + 0.85, y: SY + 1.2, z: SZ - 0.15, w: 1.2, h: 1.1 });
  }
  places.push({
    key: `marie|${shot.id}|${pose}`,
    draw: (p) => bodyFront(p, MARIE_OUTFIT, { mode: "stand", expr: shot.id >= 6 && shot.id <= 8 ? "shock" : shot.id >= 9 ? "grin" : "smile", blink: blink(1), wave: shot.id === 3 ? 0.75 : 0.4 }),
    x: SX - 0.15,
    y: SY,
    z: SZ + 0.25,
  });
  places.push({
    key: `pierre|${pose}`,
    draw: (p) => bodyFront(p, PIERRE_OUTFIT, { mode: "stand", expr: shot.id >= 6 ? "grin" : "smile", blink: blink(2), wave: 0.35 }),
    x: SX + 0.65,
    y: SY,
    z: SZ + 0.35,
  });
  rig.watchDial.visible = shot.id === 13 || shot.id === 14;
  rig.atomParticles.forEach((pt, i) => {
    pt.visible = shot.id >= 11 && shot.id <= 14;
    const ang = t * 2.6 + i * 1.25;
    const rad = ((t * 1.4 + i * 0.2) % 1) * 1.4;
    pt.position.set(Math.cos(ang) * rad, 1.25 + Math.sin(ang) * rad, 0.15);
  });
  if (shot.id >= 11 && shot.id <= 14) {
    places.push({ key: `cuPk|${pose}`, draw: (p) => bodyFront(p, KID, { mode: "stand", expr: "grin", wave: 0.6 }), x: PX - 1.5, y: PY, z: PZ + 0.15, scale: 0.84 });
  }
}
