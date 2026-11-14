// Modular 3D Scenes + Choreography for Batch 2:
// FoucaultShort, HertzShort, BernoulliShort, HookeShort, FaradayMotorShort (homopolar), EdisonTeslaBulbShort (blackbody)
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
  fxStars,
  Outfit,
  Expr,
} from "../../bridge/toon";
import { V3, FPS, clamp01 } from "../../bridge/story";
import type { ExtraPlace, ExtraFx } from "./extraEpisodes";

export type Batch2EpId = "foucault" | "hertz" | "bernoulli" | "hooke" | "homopolar" | "blackbody";

const SCI_COAT: Outfit = { jacket: "#333947", pants: "#222630", boots: INK, hat: "hair", hair: "#4a3c31", buttons: "#d9c27a" };
const SCI_BROWN: Outfit = { jacket: "#5e3d2b", pants: "#2e241f", boots: INK, hat: "hair", hair: "#2b211a", buttons: "#e2b857" };
const SMITH_OUTFIT: Outfit = { jacket: "#422c26", pants: "#241d1b", boots: INK, hat: "cap", cap: "#5e463a", build: "stout" };

export interface Batch2Rig {
  pendulumPivot: THREE.Group;
  pendulumSandRing: THREE.Mesh;
  pegs: THREE.Mesh[];
  sparkPrimary: THREE.Mesh;
  sparkLoop: THREE.Mesh;
  waveRings: THREE.Mesh[];
  wingMesh: THREE.Mesh;
  airArrows: THREE.Mesh[];
  balloonL: THREE.Mesh;
  balloonR: THREE.Mesh;
  scopeGroup: THREE.Group;
  microbeDrop: THREE.Mesh;
  microbes: THREE.Mesh[];
  motorWirePivot: THREE.Group;
  motorFieldRings: THREE.Mesh[];
  evWheel: THREE.Group;
  forgeBar: THREE.Mesh;
  forgeMat: THREE.MeshBasicMaterial;
  quantaPackets: THREE.Mesh[];
}

export function buildBatch2Shots(ep: Batch2EpId, stage: V3, park: V3) {
  const [sx, sy, sz] = stage;
  const [px, py, pz] = park;
  const B = [0, 140, 280, 420, 560, 700, 840, 980, 1120, 1260, 1400, 1540, 1680, 1820, 1960, 2100];
  const S = (id: number, light: "day" | "golden", cInf: number, pos0: V3, look0: V3, pos1: V3, look1: V3, fov = 44) => ({
    id, a: B[id - 1], b: B[id], light, cInf, pos0, look0, pos1, look1, fov,
  });

  // Consistent 15-shot cinematic staging tailored to Stage (S01-S10, S15) & Park Analogy (S11-S14)
  return [
    S(1, "day", 7, [sx + 0.5, sy + 1.85, sz + 7.2], [sx, sy + 1.4, sz], [sx + 0.1, sy + 1.7, sz + 6.0], [sx, sy + 1.4, sz], 46),
    S(2, "day", 8, [sx - 0.7, sy + 1.6, sz + 5.6], [sx - 0.2, sy + 1.25, sz - 0.2], [sx - 0.3, sy + 1.5, sz + 4.8], [sx - 0.2, sy + 1.25, sz - 0.2]),
    S(3, "day", 8, [sx + 1.2, sy + 1.65, sz + 5.8], [sx + 0.2, sy + 1.25, sz], [sx + 0.7, sy + 1.5, sz + 4.9], [sx + 0.2, sy + 1.25, sz]),
    S(4, "day", 8, [sx + 0.2, sy + 1.7, sz + 5.4], [sx, sy + 1.25, sz - 0.2], [sx - 0.1, sy + 1.55, sz + 4.6], [sx, sy + 1.25, sz - 0.2]),
    S(5, "day", 8, [sx - 0.5, sy + 1.65, sz + 5.4], [sx, sy + 1.25, sz - 0.2], [sx, sy + 1.5, sz + 4.5], [sx, sy + 1.25, sz - 0.2]),
    S(6, "day", 8, [sx + 0.7, sy + 1.65, sz + 5.2], [sx, sy + 1.25, sz - 0.2], [sx + 0.3, sy + 1.5, sz + 4.3], [sx, sy + 1.25, sz - 0.2]),
    S(7, "day", 8, [sx + 1.3, sy + 1.55, sz + 5.6], [sx + 0.3, sy + 1.25, sz + 0.1], [sx + 0.8, sy + 1.45, sz + 4.7], [sx + 0.3, sy + 1.25, sz + 0.1]),
    S(8, "day", 9, [sx - 0.3, sy + 1.55, sz + 4.8], [sx, sy + 1.2, sz - 0.2], [sx + 0.1, sy + 1.45, sz + 4.1], [sx, sy + 1.2, sz - 0.2]),
    S(9, "day", 8, [sx + 0.4, sy + 1.65, sz + 5.4], [sx, sy + 1.25, sz], [sx - 0.1, sy + 1.5, sz + 4.5], [sx, sy + 1.25, sz]),
    S(10, "day", 8, [sx + 1.0, sy + 1.65, sz + 6.0], [sx + 0.2, sy + 1.25, sz], [sx + 0.4, sy + 1.5, sz + 5.0], [sx + 0.2, sy + 1.25, sz]),
    S(11, "golden", 7, [px - 0.6, py + 1.7, pz - 6.0], [px, py + 1.3, pz], [px - 0.2, py + 1.55, pz - 5.0], [px, py + 1.3, pz]),
    S(12, "golden", 8, [px + 0.3, py + 1.6, pz - 5.4], [px, py + 1.25, pz], [px, py + 1.45, pz - 4.6], [px, py + 1.25, pz]),
    S(13, "golden", 8, [px - 0.4, py + 1.7, pz - 5.6], [px, py + 1.3, pz], [px, py + 1.55, pz - 4.7], [px, py + 1.3, pz]),
    S(14, "golden", 8, [px + 0.4, py + 1.7, pz - 5.6], [px, py + 1.3, pz], [px + 0.1, py + 1.55, pz - 4.7], [px, py + 1.3, pz]),
    S(15, "day", 6, [sx - 0.4, sy + 1.8, sz + 6.4], [sx, sy + 1.3, sz], [sx + 0.4, sy + 2.4, sz + 8.4], [sx, sy + 1.4, sz], 46),
  ];
}

export function buildBatch2Props(
  ep: Batch2EpId,
  stageGroup: THREE.Group,
  analogyGroup: THREE.Group,
  mats: { wood: THREE.Material; stone: THREE.Material; iron: THREE.Material; copper: THREE.Material; brass: THREE.Material; glass: THREE.Material; red: THREE.Material; paper: THREE.Material }
): Batch2Rig {
  const mk = () => new THREE.Mesh();
  const mg = () => new THREE.Group();
  const mBlue = twoTone(new THREE.MeshLambertMaterial({ color: "#3b76c4" }));
  const mCyan = new THREE.MeshBasicMaterial({ color: new THREE.Color(1.0, 2.8, 5.2) });
  const mAir = new THREE.MeshBasicMaterial({ color: new THREE.Color(0.9, 2.0, 3.2), transparent: true, opacity: 0.72 });
  const rig: Batch2Rig = {
    pendulumPivot: mg(), pendulumSandRing: mk(), pegs: [],
    sparkPrimary: mk(), sparkLoop: mk(), waveRings: [],
    wingMesh: mk(), airArrows: [], balloonL: mk(), balloonR: mk(),
    scopeGroup: mg(), microbeDrop: mk(), microbes: [],
    motorWirePivot: mg(), motorFieldRings: [], evWheel: mg(),
    forgeBar: mk(), forgeMat: new THREE.MeshBasicMaterial({ color: "#2b2422" }), quantaPackets: [],
  };

  if (ep === "foucault") {
    const marble = new THREE.Mesh(new THREE.CylinderGeometry(2.6, 2.6, 0.08, 32), mats.paper);
    marble.position.set(0, 0.04, -0.3);
    rig.pendulumSandRing = new THREE.Mesh(new THREE.TorusGeometry(1.5, 0.12, 8, 28), mats.stone);
    rig.pendulumSandRing.rotation.x = Math.PI / 2;
    rig.pendulumSandRing.position.set(0, 0.12, -0.3);
    const wire = new THREE.Mesh(new THREE.CylinderGeometry(0.02, 0.02, 4.2, 8), mats.iron);
    wire.position.y = -2.1;
    const bob = new THREE.Mesh(new THREE.SphereGeometry(0.32, 20, 16), mats.brass);
    bob.position.y = -4.2;
    rig.pendulumPivot.add(wire, bob);
    rig.pendulumPivot.position.set(0, 4.75, -0.3);
    stageGroup.add(marble, rig.pendulumSandRing, rig.pendulumPivot);
    for (let i = 0; i < 6; i++) {
      const ang = (i / 6) * Math.PI * 2;
      const peg = new THREE.Mesh(new THREE.CylinderGeometry(0.05, 0.06, 0.28, 8), mats.red);
      peg.position.set(Math.cos(ang) * 1.5, 0.24, -0.3 + Math.sin(ang) * 1.5);
      rig.pegs.push(peg);
      stageGroup.add(peg);
    }
    const disk = new THREE.Mesh(new THREE.CylinderGeometry(1.4, 1.4, 0.14, 24), mats.wood);
    disk.position.set(0, 0.08, 0);
    analogyGroup.add(disk);
  } else if (ep === "hertz") {
    const darkLab = new THREE.Mesh(new THREE.BoxGeometry(7.2, 4.4, 0.2), twoTone(new THREE.MeshLambertMaterial({ color: "#141824" })));
    darkLab.position.set(0, 2.2, -1.7);
    const s1 = new THREE.Mesh(new THREE.SphereGeometry(0.24, 16, 12), mats.brass);
    s1.position.set(-1.1, 1.25, -0.2);
    const s2 = new THREE.Mesh(new THREE.SphereGeometry(0.24, 16, 12), mats.brass);
    s2.position.set(-0.6, 1.25, -0.2);
    rig.sparkPrimary = new THREE.Mesh(new THREE.SphereGeometry(0.14, 10, 8), mCyan);
    rig.sparkPrimary.position.set(-0.85, 1.25, -0.2);
    rig.sparkPrimary.layers.set(NOINK);
    const loop = new THREE.Mesh(new THREE.TorusGeometry(0.48, 0.045, 10, 22), mats.copper);
    loop.position.set(1.15, 1.25, -0.2);
    rig.sparkLoop = new THREE.Mesh(new THREE.SphereGeometry(0.12, 10, 8), mCyan);
    rig.sparkLoop.position.set(1.15, 0.77, -0.2);
    rig.sparkLoop.layers.set(NOINK);
    stageGroup.add(darkLab, s1, s2, rig.sparkPrimary, loop, rig.sparkLoop);
    for (let i = 0; i < 3; i++) {
      const rw = new THREE.Mesh(new THREE.TorusGeometry(0.32 + i * 0.2, 0.03, 8, 20), mCyan);
      rw.rotation.y = Math.PI / 2;
      rw.layers.set(NOINK);
      rig.waveRings.push(rw);
      stageGroup.add(rw);
    }
    const pond = new THREE.Mesh(new THREE.CylinderGeometry(1.5, 1.5, 0.1, 24), mBlue);
    pond.position.set(0, 0.05, 0);
    analogyGroup.add(pond);
  } else if (ep === "bernoulli") {
    rig.balloonL = new THREE.Mesh(new THREE.SphereGeometry(0.32, 16, 12), mats.red);
    rig.balloonR = new THREE.Mesh(new THREE.SphereGeometry(0.32, 16, 12), mBlue);
    rig.wingMesh = new THREE.Mesh(new THREE.BoxGeometry(1.75, 0.22, 0.85), mats.paper);
    rig.wingMesh.position.set(0, 1.45, -0.2);
    stageGroup.add(rig.balloonL, rig.balloonR, rig.wingMesh);
    for (let i = 0; i < 4; i++) {
      const ar = new THREE.Mesh(new THREE.CylinderGeometry(0.03, 0.06, 0.45, 8), mAir);
      ar.rotation.z = Math.PI / 2;
      ar.layers.set(NOINK);
      rig.airArrows.push(ar);
      stageGroup.add(ar);
    }
    const goal = new THREE.Mesh(new THREE.TorusGeometry(0.85, 0.06, 8, 18, Math.PI), mats.paper);
    goal.position.set(0, 0.1, 0);
    analogyGroup.add(goal);
  } else if (ep === "hooke") {
    const tube = new THREE.Mesh(new THREE.CylinderGeometry(0.14, 0.18, 1.35, 14), mats.brass);
    tube.rotation.z = 0.25;
    tube.position.set(-0.6, 1.5, -0.2);
    const stand = new THREE.Mesh(new THREE.BoxGeometry(0.65, 0.18, 0.55), mats.wood);
    stand.position.set(-0.6, 0.85, -0.2);
    rig.scopeGroup.add(tube, stand);
    rig.microbeDrop = new THREE.Mesh(new THREE.SphereGeometry(1.05, 24, 18), twoTone(new THREE.MeshPhongMaterial({ color: "#68c7d9", transparent: true, opacity: 0.48 }), 0.15));
    rig.microbeDrop.position.set(0.6, 1.45, -0.3);
    stageGroup.add(rig.scopeGroup, rig.microbeDrop);
    const mGreen = twoTone(new THREE.MeshLambertMaterial({ color: "#4aa64e" }));
    for (let i = 0; i < 5; i++) {
      const m = new THREE.Mesh(new THREE.SphereGeometry(0.12, 10, 8), i % 2 === 0 ? mGreen : mats.red);
      rig.microbes.push(m);
      stageGroup.add(m);
    }
    const lens = new THREE.Mesh(new THREE.CylinderGeometry(0.65, 0.65, 0.12, 20), mats.glass);
    lens.rotation.x = Math.PI / 2;
    lens.position.set(0, 1.3, 0);
    analogyGroup.add(lens);
  } else if (ep === "homopolar") {
    const bowl = new THREE.Mesh(new THREE.CylinderGeometry(0.85, 0.72, 0.35, 22), mats.glass);
    bowl.position.set(-0.4, 0.95, -0.2);
    const mag = new THREE.Mesh(new THREE.CylinderGeometry(0.16, 0.16, 0.65, 14), mats.red);
    mag.position.set(-0.4, 1.15, -0.2);
    const wSeg = new THREE.Mesh(new THREE.CylinderGeometry(0.03, 0.03, 0.85, 8), mats.copper);
    wSeg.rotation.z = -0.38;
    wSeg.position.set(0.18, -0.4, 0);
    rig.motorWirePivot.add(wSeg);
    rig.motorWirePivot.position.set(-0.4, 1.85, -0.2);
    stageGroup.add(bowl, mag, rig.motorWirePivot);
    for (let i = 0; i < 3; i++) {
      const mr = new THREE.Mesh(new THREE.TorusGeometry(0.45 + i * 0.18, 0.025, 8, 20), mCyan);
      mr.rotation.x = Math.PI / 2;
      mr.position.set(-0.4, 1.15 + i * 0.18, -0.2);
      mr.layers.set(NOINK);
      rig.motorFieldRings.push(mr);
      stageGroup.add(mr);
    }
    const tire = new THREE.Mesh(new THREE.TorusGeometry(0.65, 0.18, 12, 22), mats.iron);
    rig.evWheel.add(tire);
    rig.evWheel.position.set(0, 1.25, 0);
    analogyGroup.add(rig.evWheel);
  } else {
    // blackbody
    const darkRoom = new THREE.Mesh(new THREE.BoxGeometry(7.2, 4.4, 0.2), twoTone(new THREE.MeshLambertMaterial({ color: "#191518" })));
    darkRoom.position.set(0, 2.2, -1.7);
    const anvil = new THREE.Mesh(new THREE.BoxGeometry(1.3, 0.75, 0.75), mats.iron);
    anvil.position.set(-0.4, 0.38, -0.2);
    rig.forgeBar = new THREE.Mesh(new THREE.BoxGeometry(1.4, 0.28, 0.28), rig.forgeMat);
    rig.forgeBar.position.set(-0.4, 0.92, -0.2);
    rig.forgeBar.layers.set(NOINK);
    stageGroup.add(darkRoom, anvil, rig.forgeBar);
    const colors = [new THREE.Color(3.5, 0.6, 0.4), new THREE.Color(3.5, 2.5, 0.5), new THREE.Color(1.0, 2.5, 4.5)];
    for (let i = 0; i < 6; i++) {
      const q = new THREE.Mesh(new THREE.SphereGeometry(0.11, 10, 8), new THREE.MeshBasicMaterial({ color: colors[i % 3] }));
      q.layers.set(NOINK);
      rig.quantaPackets.push(q);
      stageGroup.add(q);
    }
    const starSphere = new THREE.Mesh(new THREE.SphereGeometry(0.55, 18, 14), new THREE.MeshBasicMaterial({ color: new THREE.Color(1.2, 2.6, 4.8) }));
    starSphere.position.set(0, 1.45, 0);
    starSphere.layers.set(NOINK);
    analogyGroup.add(starSphere);
  }

  return rig;
}

export function updateBatch2Episode(
  ep: Batch2EpId,
  f: number,
  shot: { id: number; a: number; b: number },
  rig: Batch2Rig,
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

  if (ep === "foucault") {
    rig.pendulumPivot.rotation.z = 0.28 * Math.sin(t * 2.2);
    rig.pendulumPivot.rotation.y = t * 0.25;
    rig.pegs.forEach((p, i) => {
      const fallen = shot.id >= 8 && i < Math.floor(((f - 980) / 140) + 2);
      p.rotation.z = fallen ? 1.35 : 0;
    });
  } else if (ep === "hertz") {
    const on = shot.id >= 4 && shot.id <= 10;
    rig.sparkPrimary.visible = on && f % 2 === 0;
    rig.sparkLoop.visible = shot.id >= 6 && shot.id <= 10 && f % 3 === 0;
    rig.waveRings.forEach((w, i) => {
      w.visible = on;
      const p = ((t * 1.5 + i * 0.33) % 1);
      w.position.set(-0.6 + p * 1.6, 1.25, -0.2);
    });
    if (rig.sparkLoop.visible) {
      fxList.push({ key: `hzS|${f % 3}`, cw: 180, ch: 180, draw: (p) => fxStars(p, (f % 10) / 10), x: SX + 1.15, y: SY + 0.85, z: SZ - 0.1, w: 0.9, h: 0.9 });
    }
  } else if (ep === "bernoulli") {
    const closeU = shot.id === 4 || shot.id === 5 ? 0.38 : 0.72;
    rig.balloonL.position.set(-closeU, 1.25 + 0.08 * Math.sin(t * 4), -0.2);
    rig.balloonR.position.set(closeU, 1.25 + 0.08 * Math.cos(t * 4), -0.2);
    rig.wingMesh.position.y = shot.id >= 6 && shot.id <= 9 ? 1.55 + 0.18 * Math.sin(t * 3) : 1.3;
    rig.airArrows.forEach((a, i) => {
      const p = ((t * 2.2 + i * 0.25) % 1);
      a.position.set(-1.3 + p * 2.6, 1.7 + (i % 2) * 0.18, -0.2);
    });
  } else if (ep === "hooke") {
    rig.microbes.forEach((m, i) => {
      m.position.set(0.6 + Math.sin(t * 2.5 + i * 1.4) * 0.55, 1.45 + Math.cos(t * 3.1 + i) * 0.45, -0.25);
    });
    if (shot.id >= 6 && shot.id <= 9 && f % 6 < 3) {
      fxList.push({ key: `hkS|${f % 3}`, cw: 180, ch: 180, draw: (p) => fxStars(p, (f % 10) / 10), x: SX + 0.6, y: SY + 1.5, z: SZ - 0.1, w: 1.0, h: 1.0 });
    }
  } else if (ep === "homopolar") {
    const spin = shot.id >= 5;
    rig.motorWirePivot.rotation.y = spin ? t * 6.5 : 0;
    rig.evWheel.rotation.z = -t * 5.0;
    rig.motorFieldRings.forEach((r) => { r.visible = spin; });
    if (spin && f % 5 < 2) {
      fxList.push({ key: `hmS|${f % 3}`, cw: 180, ch: 180, draw: (p) => fxStars(p, (f % 10) / 10), x: SX - 0.4, y: SY + 1.2, z: SZ - 0.1, w: 1.0, h: 1.0 });
    }
  } else {
    const heat = clamp01((shot.id - 1) / 5);
    rig.forgeMat.color.setRGB(0.2 + heat * 3.0, 0.15 + Math.max(0, heat - 0.35) * 3.2, 0.15 + Math.max(0, heat - 0.7) * 4.5);
    rig.quantaPackets.forEach((q, i) => {
      q.visible = shot.id >= 8;
      const p = ((t * 1.6 + i * 0.16) % 1);
      q.position.set(-0.4 + Math.cos(i) * p * 1.4, 1.0 + p * 1.6, -0.2);
    });
    if (shot.id >= 3 && shot.id <= 9 && f % 6 < 3) {
      fxList.push({ key: `bbB|${f % 3}`, cw: 180, ch: 180, draw: (p) => fxBurst(p, 0.4), x: SX - 0.4, y: SY + 1.15, z: SZ - 0.1, w: 1.0, h: 0.9 });
    }
  }

  // Expressive hero scientist + reactive crowd/witnesses + park kids
  const outfit = ep === "blackbody" ? SMITH_OUTFIT : ep === "hooke" || ep === "foucault" ? SCI_BROWN : SCI_COAT;
  places.push({
    key: `b2hero|${ep}|${shot.id}|${pose}`,
    draw: (p) => bodyFront(p, outfit, { mode: "stand", expr: shot.id >= 6 && shot.id <= 9 ? "grin" : "smile", blink: blink(1), wave: 0.5 + 0.25 * Math.sin(t * 4) }),
    x: SX + 0.1,
    y: SY,
    z: SZ + 0.45,
  });
  for (let i = 0; i < 2; i++) {
    const walkIn = shot.id === 3 || shot.id === 4;
    const u = walkIn ? clamp01((f - shot.a) / 55) : 1;
    places.push({
      key: `b2cr|${i}|${walkIn && u < 0.95 ? "w" : "s"}|${pose}`,
      draw: (p) =>
        walkIn && u < 0.95
          ? bodySide(p, townsfolk(i), { mode: "march", expr: "shock", phase: (t * 2.8 + i * 0.3) % 1 })
          : bodyFront(p, townsfolk(i), { mode: "stand", expr: shot.id >= 7 ? "grin" : "smile", wave: 0.55 }),
      x: SX + 0.95 + i * 0.55 + (1 - u) * 1.8,
      y: SY,
      z: SZ + 0.65 + i * 0.15,
      mirror: walkIn && u < 0.95,
    });
  }
  if (shot.id >= 11 && shot.id <= 14) {
    places.push({ key: `b2pkK|${pose}`, draw: (p) => bodyFront(p, KID, { mode: "stand", expr: "grin", wave: 0.6 }), x: PX - 1.45, y: PY, z: PZ + 0.15, scale: 0.84 });
    places.push({ key: `b2pkP|${pose}`, draw: (p) => bodyFront(p, PARENT, { mode: "stand", expr: "smile" }), x: PX + 1.45, y: PY, z: PZ + 0.15 });
  }
}
