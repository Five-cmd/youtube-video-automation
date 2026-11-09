// Multi-episode 3D Toon World + 2D Bean-Head Character Physics Engine for:
//   1. CavendishShort ("The Man Who Left the Room to Weigh the World" - Universal Gravitation, 1797)
//   2. MagdeburgShort ("Sixteen Horses Couldn't Pull Apart Empty Air" - Atmospheric Pressure, 1654)
//   3. FaradayShort   ("The Man Who Climbed Into a Metal Cage to Get Struck by Lightning" - Electromagnetism, 1836)
// Reuses the verified look-match pipeline from ../bridge/ (InkPass -> LensBlur -> Bloom -> NEUTRAL tone map -> Grade,
// two-tone Lambert/Phong materials, HD painted textures, and Pen 2D character cards on the NOINK layer).
import React, { useEffect, useMemo, useState } from "react";
import * as THREE from "three";
import { AbsoluteFill, continueRender, delayRender, useCurrentFrame } from "remotion";
import { ThreeCanvas } from "@remotion/three";
import { useThree } from "@react-three/fiber";
import { EffectComposer } from "@react-three/postprocessing";
import { BlendFunction, BloomEffect, ToneMappingEffect, ToneMappingMode } from "postprocessing";
import { World, loadKit } from "../bridge/world";
import { InkPass, NOINK, noInkFallback } from "../bridge/ink";
import { LensBlur } from "../bridge/lensblur";
import { GradeEffect, GRADES, GRADE_STRENGTH, gradeFor } from "../bridge/grade";
import { Kit, V, Strand } from "../bridge/build";
import { twoTone } from "../bridge/shade";
import { beam, stone } from "../bridge/paint";
import { Actor, Fx, Pool } from "../bridge/cast";
import { Pen, INK, bodyFront, bodySide, townsfolk, OFFICER, KID, PARENT, fxBurst, fxStars, fxBlob, Outfit, Expr } from "../bridge/toon";
import { D0, FPS, V3, clamp01, smooth, glide } from "../bridge/story";

export type EpId = "cavendish" | "magdeburg" | "faraday";
export const EP_FRAMES: Record<EpId, number> = {
  cavendish: 2070, // 69.0 s @ 30 fps
  magdeburg: 1965, // 65.5 s @ 30 fps
  faraday: 2010,   // 67.0 s @ 30 fps
};

// Plaza stage on the cobblestone riverfront promenade (clear sightlines, town + river backdrop)
const SX = 18.0, SY = D0, SZ = -33.2;
// Golden-hour park stage for the "You see," everyday analogy (shots 11-12)
const PX = 64.0, PY = D0, PZ = -72.0;

type EpShot = { id: number; a: number; b: number; light: "day" | "golden"; cInf: number; pos0: V3; look0: V3; pos1: V3; look1: V3; fov?: number; roll?: number; kickAt?: number };

const makeShots = (total: number, stage: V3, park: V3): EpShot[] => {
  const [sx, sy, sz] = stage, [px, py, pz] = park;
  return [
    // 1. Hook (0 - 130f, ends with 4-frame white flash)
    { id: 1, a: 0, b: 130, light: "day", cInf: 14, pos0: [sx - 1.2, sy + 1.5, sz + 5.6], look0: [sx, sy + 1.35, sz], pos1: [sx - 0.6, sy + 1.45, sz + 3.8], look1: [sx, sy + 1.35, sz], fov: 38 },
    // 2. Setting wide town + riverfront establish (130 - 285f)
    { id: 2, a: 130, b: 285, light: "day", cInf: 0, pos0: [sx + 11.5, sy + 5.2, sz + 14.0], look0: [sx - 1.0, sy + 1.8, sz - 2.0], pos1: [sx + 7.5, sy + 3.4, sz + 10.2], look1: [sx, sy + 1.5, sz], fov: 42 },
    // 3. Apparatus close inspection (285 - 445f)
    { id: 3, a: 285, b: 445, light: "day", cInf: 12, pos0: [sx + 2.4, sy + 1.65, sz + 4.2], look0: [sx, sy + 1.4, sz], pos1: [sx + 1.6, sy + 1.55, sz + 3.3], look1: [sx, sy + 1.4, sz], fov: 36 },
    // 4. Escalation beat 1: scale / giant masses / horses / generator (445 - 565f)
    { id: 4, a: 445, b: 565, light: "day", cInf: 10, pos0: [sx - 3.8, sy + 1.4, sz + 5.8], look0: [sx - 0.5, sy + 1.3, sz], pos1: [sx - 2.6, sy + 1.35, sz + 4.6], look1: [sx - 0.2, sy + 1.3, sz], fov: 40, kickAt: 455 },
    // 5. Escalation beat 2: crowd reaction / mocking / doubt (565 - 690f)
    { id: 5, a: 565, b: 690, light: "day", cInf: 11, pos0: [sx + 4.8, sy + 1.5, sz + 4.5], look0: [sx + 1.5, sy + 1.3, sz + 0.5], pos1: [sx + 3.6, sy + 1.45, sz + 3.7], look1: [sx + 0.8, sy + 1.3, sz + 0.2], fov: 38 },
    // 6. Escalation beat 3: rising tension (690 - 835f)
    { id: 6, a: 690, b: 835, light: "day", cInf: 13, pos0: [sx - 2.2, sy + 1.8, sz + 4.9], look0: [sx, sy + 1.4, sz], pos1: [sx - 1.2, sy + 1.6, sz + 3.6], look1: [sx, sy + 1.4, sz], fov: 36, roll: 0.065 },
    // 7. Peak strain right before the snap (835 - 985f)
    { id: 7, a: 835, b: 985, light: "day", cInf: 14, pos0: [sx + 0.8, sy + 1.3, sz + 3.9], look0: [sx, sy + 1.35, sz], pos1: [sx + 0.3, sy + 1.3, sz + 2.9], look1: [sx, sy + 1.35, sz], fov: 35, roll: -0.07 },
    // 8. THE SNAP: physical climax / bolt / valve / deflection (985 - 1135f)
    { id: 8, a: 985, b: 1135, light: "day", cInf: 12, pos0: [sx - 0.4, sy + 1.55, sz + 4.8], look0: [sx, sy + 1.35, sz], pos1: [sx + 0.5, sy + 1.45, sz + 3.8], look1: [sx, sy + 1.35, sz], fov: 38, kickAt: 1005 },
    // 9. Deadpan line 1: "Luckily..." (1135 - 1220f)
    { id: 9, a: 1135, b: 1220, light: "day", cInf: 14, pos0: [sx - 1.8, sy + 1.4, sz + 3.6], look0: [sx - 0.3, sy + 1.3, sz], pos1: [sx - 1.4, sy + 1.4, sz + 3.2], look1: [sx - 0.3, sy + 1.3, sz], fov: 35 },
    // 10. Deadpan line 2: "Unluckily..." (1220 - 1310f)
    { id: 10, a: 1220, b: 1310, light: "day", cInf: 11, pos0: [sx + 2.8, sy + 1.5, sz + 4.6], look0: [sx + 0.6, sy + 1.25, sz], pos1: [sx + 2.2, sy + 1.45, sz + 4.0], look1: [sx + 0.4, sy + 1.25, sz], fov: 38 },
    // 11. Pivot "You see," in Golden Hour light (1310 - 1425f)
    { id: 11, a: 1310, b: 1425, light: "golden", cInf: 8, pos0: [px - 3.5, py + 1.7, pz + 6.5], look0: [px, py + 1.4, pz], pos1: [px - 2.2, py + 1.55, pz + 5.0], look1: [px, py + 1.4, pz], fov: 38 },
    // 12. Everyday Analogy demonstration in the Park (1425 - 1640f)
    { id: 12, a: 1425, b: 1640, light: "golden", cInf: 13, pos0: [px + 1.8, py + 1.45, pz + 4.4], look0: [px, py + 1.3, pz], pos1: [px + 0.6, py + 1.4, pz + 3.3], look1: [px, py + 1.3, pz], fov: 35 },
    // 13. Connecting analogy back to the apparatus in Golden Light (1640 - 1755f)
    { id: 13, a: 1640, b: 1755, light: "golden", cInf: 10, pos0: [sx - 2.6, sy + 1.7, sz + 5.2], look0: [sx, sy + 1.4, sz], pos1: [sx - 1.5, sy + 1.55, sz + 4.0], look1: [sx, sy + 1.4, sz], fov: 38 },
    // 14. Scientific Consequence (1755 - 1880f)
    { id: 14, a: 1755, b: 1880, light: "day", cInf: 10, pos0: [sx + 2.2, sy + 1.55, sz + 4.8], look0: [sx, sy + 1.35, sz], pos1: [sx + 1.2, sy + 1.5, sz + 3.8], look1: [sx, sy + 1.35, sz], fov: 38 },
    // 15. Callback Twist payoff (1880 - total)
    { id: 15, a: 1880, b: total, light: "day", cInf: 8, pos0: [sx - 0.5, sy + 1.6, sz + 5.0], look0: [sx, sy + 1.3, sz], pos1: [sx + 0.4, sy + 2.2, sz + 7.2], look1: [sx, sy + 1.3, sz], fov: 40 },
  ];
};

// Outfits for the historical scientists (drawn with the same Pen bean-head system)
const CAVENDISH_OUTFIT: Outfit = { jacket: "#3b2c47", pants: "#2b2630", boots: INK, hat: "tophat", buttons: "#d8cfa8" };
const GUERICKE_OUTFIT: Outfit = { jacket: "#6e2c26", pants: "#2f2a28", boots: INK, hat: "tophat", buttons: "#e2b857", sash: "#e2b857" };
const FARADAY_OUTFIT: Outfit = { jacket: "#243447", pants: "#252830", boots: INK, hat: "hair", hair: "#4a382b", buttons: "#e8e4dc" };
const LAB_OUTFIT: Outfit = { jacket: "#eceef2", pants: "#2d333b", boots: INK, hat: "hair", hair: "#3d332a", buttons: "#5b7691" };

const makeBloom = () => {
  const b = new BloomEffect({ blendFunction: BlendFunction.ADD, intensity: 0.5, luminanceThreshold: 1.0, luminanceSmoothing: 0.2, mipmapBlur: true, levels: 6, radius: 0.6 });
  const mip = b.mipmapBlurPass;
  const setSize = mip.setSize.bind(mip);
  mip.setSize = (w: number, h: number) => setSize(Math.round((1920 * w) / Math.max(h, 1)), 1920);
  return b;
};

const useKit = () => {
  const [kit, setKit] = useState<Kit | null>(null);
  const [handle] = useState(() => delayRender("physics kit"));
  useEffect(() => { loadKit().then((k) => { setKit(k); continueRender(handle); }); }, [handle]);
  return kit;
};

class EpisodeRig {
  group = new THREE.Group();
  analogyGroup = new THREE.Group();
  actors: Actor[] = [];
  fxs: Fx[] = [];
  // Cavendish parts
  torsionPivot = new THREE.Group();
  bigBeamPivot = new THREE.Group();
  magnetPaper = new THREE.Mesh();
  // Magdeburg parts
  hemiL = new THREE.Mesh();
  hemiR = new THREE.Mesh();
  piston = new THREE.Mesh();
  ropeL: Strand;
  ropeR: Strand;
  plunger = new THREE.Group();
  // Faraday parts
  wheel = new THREE.Mesh();
  boltMesh = new THREE.Mesh();
  leafL = new THREE.Mesh();
  leafR = new THREE.Mesh();

  constructor(public ep: EpId, root: THREE.Group) {
    this.group.position.set(SX, SY, SZ);
    this.analogyGroup.position.set(PX, PY, PZ);
    root.add(this.group, this.analogyGroup);

    const mWood = twoTone(new THREE.MeshLambertMaterial({ map: beam() }));
    const mStone = twoTone(new THREE.MeshLambertMaterial({ map: stone("epStone") }));
    const mIron = twoTone(new THREE.MeshPhongMaterial({ color: "#383c46", specular: "#8a8a8a", shininess: 55 }), 0.15);
    const mLead = twoTone(new THREE.MeshPhongMaterial({ color: "#525866", specular: "#9aa0ad", shininess: 40 }), 0.15);
    const mCopper = twoTone(new THREE.MeshPhongMaterial({ color: "#c96e3c", specular: "#f0b080", shininess: 65 }), 0.18);
    const mBrass = twoTone(new THREE.MeshPhongMaterial({ color: "#d4a843", specular: "#ffe29a", shininess: 75 }), 0.2);
    const mGlass = twoTone(new THREE.MeshPhongMaterial({ color: "#8ec5d6", specular: "#ffffff", shininess: 90, transparent: true, opacity: 0.65 }), 0.2);
    const mRed = twoTone(new THREE.MeshLambertMaterial({ color: "#c93b32" }));
    const mPaper = twoTone(new THREE.MeshLambertMaterial({ color: "#f3efe6" }));

    this.ropeL = new Strand(12, 0.045, mWood);
    this.ropeR = new Strand(12, 0.045, mWood);

    if (ep === "cavendish") {
      // Cutaway garden shed frame + wooden torsion box + telescope in wall
      const base = new THREE.Mesh(new THREE.BoxGeometry(4.4, 0.18, 3.2), mStone);
      base.position.set(0, 0.09, 0);
      this.group.add(base);
      for (const [x, z] of [[-2.05, -1.45], [2.05, -1.45], [-2.05, 1.45], [2.05, 1.45]]) {
        const post = new THREE.Mesh(new THREE.BoxGeometry(0.18, 3.1, 0.18), mWood);
        post.position.set(x, 1.6, z);
        this.group.add(post);
      }
      const backWall = new THREE.Mesh(new THREE.BoxGeometry(4.3, 3.0, 0.14), mWood);
      backWall.position.set(0, 1.6, -1.5);
      const leftWall = new THREE.Mesh(new THREE.BoxGeometry(0.14, 3.0, 3.1), mWood);
      leftWall.position.set(-2.05, 1.6, 0);
      const topBeam = new THREE.Mesh(new THREE.BoxGeometry(4.5, 0.22, 3.3), mWood);
      topBeam.position.set(0, 3.15, 0);
      this.group.add(backWall, leftWall, topBeam);

      // Torsion wire + 6-ft (1.8 m) rod + two small lead balls
      const wire = new THREE.Mesh(new THREE.CylinderGeometry(0.018, 0.018, 1.55, 8), mBrass);
      wire.position.set(0, 2.3, 0);
      const rod = new THREE.Mesh(new THREE.BoxGeometry(1.9, 0.07, 0.07), mWood);
      rod.position.set(0, 1.5, 0);
      this.torsionPivot.add(wire, rod);
      for (const s of [-1, 1]) {
        const sb = new THREE.Mesh(new THREE.SphereGeometry(0.14, 20, 16), mRed);
        sb.position.set(s * 0.92, 1.5, 0);
        this.torsionPivot.add(sb);
      }
      // Two giant 348-lb lead spheres on rotatable suspension struts
      const bigBar = new THREE.Mesh(new THREE.BoxGeometry(2.1, 0.12, 0.12), mIron);
      bigBar.position.set(0, 2.85, 0);
      this.bigBeamPivot.add(bigBar);
      for (const s of [-1, 1]) {
        const strut = new THREE.Mesh(new THREE.CylinderGeometry(0.035, 0.035, 1.35, 10), mIron);
        strut.position.set(s * 0.92, 2.18, s * 0.36);
        const bigBall = new THREE.Mesh(new THREE.SphereGeometry(0.42, 24, 18), mLead);
        bigBall.position.set(s * 0.92, 1.48, s * 0.36);
        this.bigBeamPivot.add(strut, bigBall);
      }
      this.group.add(this.torsionPivot, this.bigBeamPivot);

      // Brass telescope outside the left shed wall + tripod
      const scope = new THREE.Mesh(new THREE.CylinderGeometry(0.06, 0.08, 0.95, 14), mBrass);
      scope.rotation.z = Math.PI / 2;
      scope.position.set(-2.55, 1.48, 0.25);
      const tripod = new THREE.Mesh(new THREE.ConeGeometry(0.35, 1.45, 6), mWood);
      tripod.position.set(-2.65, 0.72, 0.25);
      this.group.add(scope, tripod);

      // Analogy prop in the park: giant steel board + white paper + red horseshoe magnet
      const fridge = new THREE.Mesh(new THREE.BoxGeometry(1.8, 2.5, 0.35), mPaper);
      fridge.position.set(0, 1.25, -0.3);
      this.magnetPaper = new THREE.Mesh(new THREE.BoxGeometry(0.65, 0.82, 0.03), mPaper);
      this.magnetPaper.position.set(0, 1.55, -0.1);
      const mag = new THREE.Mesh(new THREE.BoxGeometry(0.32, 0.22, 0.12), mRed);
      mag.position.set(0, 1.72, -0.04);
      this.analogyGroup.add(fridge, this.magnetPaper, mag);
    }

    if (ep === "magdeburg") {
      // Pedestal cradle + two copper hemispheres + brass air pump + pulling ropes
      const table = new THREE.Mesh(new THREE.BoxGeometry(1.5, 0.95, 1.1), mWood);
      table.position.set(0, 0.48, 0);
      this.group.add(table);
      const hGeoL = new THREE.SphereGeometry(0.56, 24, 18, 0, Math.PI * 2, 0, Math.PI / 2);
      hGeoL.rotateZ(Math.PI / 2);
      const hGeoR = new THREE.SphereGeometry(0.56, 24, 18, 0, Math.PI * 2, 0, Math.PI / 2);
      hGeoR.rotateZ(-Math.PI / 2);
      this.hemiL = new THREE.Mesh(hGeoL, mCopper);
      this.hemiR = new THREE.Mesh(hGeoR, mCopper);
      const ringL = new THREE.Mesh(new THREE.TorusGeometry(0.12, 0.035, 10, 18), mBrass);
      ringL.position.set(-0.62, 0, 0);
      this.hemiL.add(ringL);
      const ringR = new THREE.Mesh(new THREE.TorusGeometry(0.12, 0.035, 10, 18), mBrass);
      ringR.position.set(0.62, 0, 0);
      this.hemiR.add(ringR);
      const valve = new THREE.Mesh(new THREE.CylinderGeometry(0.04, 0.04, 0.28, 10), mBrass);
      valve.position.set(-0.25, 0.58, 0);
      this.hemiL.add(valve);
      this.group.add(this.hemiL, this.hemiR);

      // Brass vacuum pump beside the table
      const cyl = new THREE.Mesh(new THREE.CylinderGeometry(0.16, 0.16, 0.85, 16), mBrass);
      cyl.position.set(0, 0.95, 0.72);
      this.piston = new THREE.Mesh(new THREE.BoxGeometry(0.45, 0.08, 0.08), mWood);
      this.piston.position.set(0, 1.45, 0.72);
      this.group.add(cyl, this.piston, this.ropeL.mesh, this.ropeR.mesh);

      // Analogy prop in the park: smooth tile slab + giant red rubber plunger
      const slab = new THREE.Mesh(new THREE.BoxGeometry(2.6, 0.16, 2.2), mStone);
      slab.position.set(0, 0.08, 0);
      const cup = new THREE.Mesh(new THREE.SphereGeometry(0.52, 22, 14, 0, Math.PI * 2, 0, Math.PI / 2), mRed);
      const stick = new THREE.Mesh(new THREE.CylinderGeometry(0.055, 0.055, 1.45, 12), mWood);
      stick.position.set(0, 1.15, 0);
      this.plunger.add(cup, stick);
      this.analogyGroup.add(slab, this.plunger);
    }

    if (ep === "faraday") {
      // 12-foot conducting cage on 4 glass insulator pillars + copper mesh bars
      for (const [x, z] of [[-1.5, -1.3], [1.5, -1.3], [-1.5, 1.3], [1.5, 1.3]]) {
        const leg = new THREE.Mesh(new THREE.CylinderGeometry(0.12, 0.14, 0.45, 12), mGlass);
        leg.position.set(x, 0.22, z);
        this.group.add(leg);
      }
      const floor = new THREE.Mesh(new THREE.BoxGeometry(3.3, 0.12, 2.9), mWood);
      floor.position.set(0, 0.48, 0);
      this.group.add(floor);
      // Cage frame bars (copper + iron)
      for (const [x, z] of [[-1.55, -1.35], [1.55, -1.35], [-1.55, 1.35], [1.55, 1.35]]) {
        const bar = new THREE.Mesh(new THREE.BoxGeometry(0.1, 2.85, 0.1), mCopper);
        bar.position.set(x, 1.9, z);
        this.group.add(bar);
      }
      for (const y of [0.55, 1.45, 2.35, 3.28]) {
        const topF = new THREE.Mesh(new THREE.BoxGeometry(3.2, 0.07, 0.07), mCopper);
        topF.position.set(0, y, 1.35);
        const topB = new THREE.Mesh(new THREE.BoxGeometry(3.2, 0.07, 0.07), mCopper);
        topB.position.set(0, y, -1.35);
        const sideL = new THREE.Mesh(new THREE.BoxGeometry(0.07, 0.07, 2.8), mCopper);
        sideL.position.set(-1.55, y, 0);
        const sideR = new THREE.Mesh(new THREE.BoxGeometry(0.07, 0.07, 2.8), mCopper);
        sideR.position.set(1.55, y, 0);
        this.group.add(topF, topB, sideL, sideR);
      }
      // Gold-leaf electroscope on a stand inside the cage
      const stand = new THREE.Mesh(new THREE.CylinderGeometry(0.06, 0.09, 1.1, 10), mWood);
      stand.position.set(-0.85, 1.05, 0.2);
      const jar = new THREE.Mesh(new THREE.CylinderGeometry(0.18, 0.18, 0.36, 14), mGlass);
      jar.position.set(-0.85, 1.75, 0.2);
      this.leafL = new THREE.Mesh(new THREE.BoxGeometry(0.02, 0.18, 0.06), mBrass);
      this.leafR = new THREE.Mesh(new THREE.BoxGeometry(0.02, 0.18, 0.06), mBrass);
      this.leafL.position.set(-0.88, 1.72, 0.2);
      this.leafR.position.set(-0.82, 1.72, 0.2);
      this.group.add(stand, jar, this.leafL, this.leafR);

      // Electrostatic generator outside left of the cage
      const genBase = new THREE.Mesh(new THREE.BoxGeometry(1.2, 0.9, 0.9), mWood);
      genBase.position.set(-3.2, 0.45, 0.2);
      this.wheel = new THREE.Mesh(new THREE.CylinderGeometry(0.75, 0.75, 0.06, 24), mGlass);
      this.wheel.rotation.x = Math.PI / 2;
      this.wheel.position.set(-3.2, 1.55, 0.2);
      const brassOrb = new THREE.Mesh(new THREE.SphereGeometry(0.24, 18, 14), mBrass);
      brassOrb.position.set(-2.35, 1.85, 0.2);
      // HDR lightning bolt mesh (luminance > 1.0 triggers BloomEffect!)
      const boltMat = new THREE.MeshBasicMaterial({ color: new THREE.Color(2.4, 3.4, 6.8) });
      this.boltMesh = new THREE.Mesh(new THREE.CylinderGeometry(0.045, 0.045, 0.95, 8), boltMat);
      this.boltMesh.rotation.z = Math.PI / 2.2;
      this.boltMesh.position.set(-1.95, 1.82, 0.2);
      this.boltMesh.layers.set(NOINK);
      this.group.add(genBase, this.wheel, brassOrb, this.boltMesh);

      // Analogy room outline in the park
      const roomFloor = new THREE.Mesh(new THREE.BoxGeometry(4.6, 0.1, 4.6), mStone);
      roomFloor.position.set(0, 0.05, 0);
      this.analogyGroup.add(roomFloor);
    }

    this.group.traverse((o) => { if (o !== this.boltMesh) { o.castShadow = true; o.receiveShadow = true; } });
    this.analogyGroup.traverse((o) => { o.castShadow = true; o.receiveShadow = true; });
  }

  private actor(root: THREE.Group, i: number) {
    while (this.actors.length <= i) this.actors.push(new Actor(root));
    return this.actors[i];
  }
  private fx(root: THREE.Group, i: number) {
    while (this.fxs.length <= i) this.fxs.push(new Fx(root));
    return this.fxs[i];
  }

  update(f: number, shot: EpShot, cam: THREE.PerspectiveCamera, world: World) {
    const t = f / FPS;
    const pool = (world as unknown as { pool: Pool }).pool;
    // Hide the bridge's marching soldiers so our physics cast takes the stage
    const wActors = (world as unknown as { actors: Actor[]; swing: Actor; fxs: Fx[] });
    for (const a of wActors.actors) a.mesh.visible = false;
    if (wActors.swing) wActors.swing.mesh.visible = false;
    for (const e of wActors.fxs) e.mesh.visible = false;

    // Camera interpolation with creeping push-in (never static >= 4f) + 7-frame decaying flip-kick on impacts
    const u = clamp01((f - shot.a) / Math.max(1, shot.b - shot.a));
    const g = glide(Math.min(1, (f - shot.a) / 28));
    const creep = u * 0.18;
    const k = clamp01(g * 0.82 + creep);
    const pos: V3 = [
      shot.pos0[0] + (shot.pos1[0] - shot.pos0[0]) * k,
      shot.pos0[1] + (shot.pos1[1] - shot.pos0[1]) * k,
      shot.pos0[2] + (shot.pos1[2] - shot.pos0[2]) * k,
    ];
    const look: V3 = [
      shot.look0[0] + (shot.look1[0] - shot.look0[0]) * k,
      shot.look0[1] + (shot.look1[1] - shot.look0[1]) * k,
      shot.look0[2] + (shot.look1[2] - shot.look0[2]) * k,
    ];
    if (shot.kickAt && f >= shot.kickAt && f < shot.kickAt + 7) {
      const df = f - shot.kickAt;
      const amp = 0.14 * Math.pow(0.65, df) * (df % 2 === 0 ? 1 : -1);
      pos[1] += amp;
      look[1] += amp * 0.6;
    }
    cam.position.set(...pos);
    cam.up.set(0, 1, 0);
    cam.lookAt(...look);
    if (shot.roll) cam.rotateZ(shot.roll * smooth(Math.min(1, (f - shot.a) / 20)));
    cam.fov = shot.fov ?? 38;
    cam.updateProjectionMatrix();
    cam.updateMatrixWorld();

    // Animate 3D physics props + stage 2D bean-head characters
    const places: { key: string; draw: (p: Pen) => void; x: number; y: number; z: number; scale?: number; mirror?: boolean }[] = [];
    const fxList: { key: string; cw: number; ch: number; draw: (p: Pen) => void; x: number; y: number; z: number; w: number; h: number; flat?: boolean }[] = [];
    const blink = (seed: number) => ((f + seed * 19) % 58) < 4;

    if (this.ep === "cavendish") {
      const torsionAng = shot.id >= 7 ? 0.22 * Math.sin(t * 1.4) : 0.06 * Math.sin(t * 0.9);
      this.torsionPivot.rotation.y = torsionAng;
      this.bigBeamPivot.rotation.y = shot.id >= 4 ? 0.18 : -0.18;
      this.magnetPaper.position.y = 1.55 + 0.03 * Math.sin(t * 3);

      // Cavendish outside peeking through telescope or locking shed
      const cavX = shot.id <= 5 ? SX - 1.3 : SX - 3.05;
      const cavExpr: Expr = shot.id === 8 ? "shock" : shot.id >= 13 ? "grin" : "nervous";
      places.push({
        key: `cav|${cavExpr}|${blink(1) ? 1 : 0}`,
        draw: (p) => bodyFront(p, CAVENDISH_OUTFIT, { mode: "stand", expr: cavExpr, blink: blink(1), look: 1, wave: 0.4 }),
        x: cavX, y: SY, z: SZ + 0.45,
      });
      // Two grown men for scale next to the giant lead spheres in shots 4-5
      if (shot.id === 4 || shot.id === 5) {
        for (const i of [0, 1]) {
          places.push({
            key: `scaleMan|${i}|${blink(i + 2) ? 1 : 0}`,
            draw: (p) => bodyFront(p, townsfolk(i + 2), { mode: "stand", expr: "shock", blink: blink(i + 2) }),
            x: SX + 1.45 + i * 0.95, y: SY, z: SZ + 0.5,
          });
        }
      }
      if (shot.id === 11 || shot.id === 12) {
        places.push({
          key: `kidMag|${blink(5) ? 1 : 0}`,
          draw: (p) => bodyFront(p, KID, { mode: "stand", expr: "grin", blink: blink(5), wave: 0.6 }),
          x: PX - 1.15, y: PY, z: PZ + 0.3, scale: 0.82,
        });
        places.push({
          key: `parMag|${blink(6) ? 1 : 0}`,
          draw: (p) => bodyFront(p, PARENT, { mode: "stand", expr: "relief", blink: blink(6) }),
          x: PX + 1.25, y: PY, z: PZ + 0.3,
        });
      }
      if (shot.id === 15) {
        // Modern scientists tiptoeing away from the shed
        const walk = (f - shot.a) * 0.025;
        for (let i = 0; i < 3; i++) {
          places.push({
            key: `lab|${i}|${Math.floor(t * 6) % 4}`,
            draw: (p) => bodySide(p, LAB_OUTFIT, { mode: "march", expr: "nervous", phase: (t * 1.5 + i * 0.3) % 1, blink: blink(i + 7) }),
            x: SX + 1.2 + i * 1.1 + walk, y: SY, z: SZ + 0.9,
          });
        }
      }
    }

    if (this.ep === "magdeburg") {
      const snapped = shot.id >= 8 && shot.id <= 10;
      const sep = snapped ? 0.55 * clamp01((f - 995) / 18) : 0;
      const strain = (shot.id >= 5 && shot.id <= 7) ? 0.03 * Math.sin(t * 22) : 0;
      this.hemiL.position.set(-sep + strain, 1.28, 0);
      this.hemiR.position.set(sep - strain, 1.28, 0);
      this.piston.position.y = 1.38 + (shot.id <= 4 ? 0.18 * Math.abs(Math.sin(t * 6)) : 0);
      this.ropeL.set(Array.from({ length: 12 }, (_, i) => V(-0.62 - sep - i * 0.45, 1.28 - (snapped ? 0.35 * Math.sin((i / 11) * Math.PI) : 0.04 * Math.sin((i / 11) * Math.PI)), 0)));
      this.ropeR.set(Array.from({ length: 12 }, (_, i) => V(0.62 + sep + i * 0.45, 1.28 - (snapped ? 0.35 * Math.sin((i / 11) * Math.PI) : 0.04 * Math.sin((i / 11) * Math.PI)), 0)));
      this.plunger.position.set(0, 0.16, 0);

      // Mayor Otto von Guericke
      places.push({
        key: `guericke|${shot.id >= 8 ? 1 : 0}|${blink(1) ? 1 : 0}`,
        draw: (p) => bodyFront(p, GUERICKE_OUTFIT, { mode: "stand", expr: shot.id >= 8 ? "grin" : "stern", blink: blink(1), wave: shot.id === 8 ? 0.7 : undefined }),
        x: SX, y: SY, z: SZ - 1.15,
      });
      // Pulling teams on left and right
      for (const side of [-1, 1]) {
        for (let k = 0; k < 4; k++) {
          const px = SX + side * (2.2 + k * 1.05);
          places.push({
            key: `puller|${side}|${k}|${Math.floor(t * 4) % 2}`,
            draw: (p) => bodySide(p, townsfolk(k + (side > 0 ? 4 : 0)), { mode: "push", expr: snapped ? "shock" : "stern", phase: (t * 2 + k * 0.25) % 1, pose: 0.85 }),
            x: px, y: SY, z: SZ + (k % 2) * 0.35, mirror: side < 0,
          });
        }
      }
      if (shot.id === 8 && f >= 995 && f < 1030) {
        fxList.push({ key: "magBurst", cw: 260, ch: 260, draw: (p) => fxBurst(p, 0.5), x: SX, y: SY + 1.5, z: SZ + 0.4, w: 1.5, h: 1.5 });
      }
      if (shot.id === 11 || shot.id === 12) {
        places.push({
          key: `plungerGuy|${blink(3) ? 1 : 0}`,
          draw: (p) => bodyFront(p, PARENT, { mode: "stand", expr: "stern", blink: blink(3), wave: 0.5 }),
          x: PX - 1.2, y: PY, z: PZ + 0.2,
        });
      }
    }

    if (this.ep === "faraday") {
      this.wheel.rotation.z = t * 5.0;
      const sparking = (shot.id >= 4 && shot.id <= 8) || shot.id === 1;
      this.boltMesh.visible = sparking && (f % 3 !== 0);
      this.leafL.rotation.z = 0; // Inside the Faraday cage, the gold leaves NEVER move!
      this.leafR.rotation.z = 0;

      // Michael Faraday standing calmly inside the 12-foot cage
      places.push({
        key: `faraday|${blink(1) ? 1 : 0}`,
        draw: (p) => bodyFront(p, FARADAY_OUTFIT, { mode: "stand", expr: "grin", blink: blink(1), wave: 0.3 }),
        x: SX + 0.2, y: SY + 0.52, z: SZ,
      });
      // Assistant cranking the lightning machine outside left
      places.push({
        key: `assist|${Math.floor(t * 6) % 2}`,
        draw: (p) => bodySide(p, OFFICER, { mode: "march", expr: sparking ? "shock" : "nervous", phase: (t * 2) % 1 }),
        x: SX - 3.95, y: SY, z: SZ + 0.25,
      });
      // Front-row audience ducking / gasping outside right
      for (let i = 0; i < 3; i++) {
        places.push({
          key: `aud|${i}|${sparking ? 1 : 0}`,
          draw: (p) => bodyFront(p, townsfolk(i + 1), { mode: "stand", expr: sparking ? "shock" : "nervous", blink: blink(i + 4) }),
          x: SX + 2.35 + i * 0.95, y: SY, z: SZ + 1.1,
        });
      }
      if (sparking) {
        fxList.push({ key: `spark|${f % 3}`, cw: 260, ch: 260, draw: (p) => fxStars(p, (f % 10) / 10), x: SX - 1.65, y: SY + 1.85, z: SZ + 0.35, w: 1.35, h: 1.35 });
      }
      // Shots 11-12 Analogy: people in a small room backing up to the outer walls, leaving the middle empty
      if (shot.id === 11 || shot.id === 12) {
        const pushU = shot.id === 11 ? clamp01((f - shot.a) / 60) : 1.0;
        const rad = 0.55 + pushU * 1.45;
        for (let i = 0; i < 8; i++) {
          const ang = (i / 8) * Math.PI * 2;
          places.push({
            key: `roomChar|${i}|${blink(i) ? 1 : 0}`,
            draw: (p) => bodyFront(p, townsfolk(i), { mode: "stand", expr: "stern", blink: blink(i) }),
            x: PX + Math.cos(ang) * rad, y: PY + 0.1, z: PZ + Math.sin(ang) * rad, scale: 0.85,
          });
        }
      }
    }

    // Bind actors + contact shadow blobs into the shared Pool
    let ai = 0, fi = 0;
    const usedA: Actor[] = [], usedF: Fx[] = [];
    for (const p of places) {
      const a = this.actor(world.root, ai++);
      const sc = p.scale ?? 1;
      a.r = pool.req(p.key, 300, 500, 0.5, p.draw);
      a.mesh.visible = true;
      a.mesh.position.set(p.x, p.y, p.z);
      a.mesh.rotation.set(0, Math.atan2(cam.position.x - p.x, cam.position.z - p.z), 0);
      a.mesh.scale.set(p.mirror ? -sc : sc, sc, sc);
      usedA.push(a);

      // Soft contact shadow blob under each character's feet
      const b = this.fx(world.root, fi++);
      b.r = pool.req("ep|blob|foot", 128, 128, 1, (pen) => fxBlob(pen, "#5e5078"));
      b.mesh.visible = true;
      b.mesh.position.set(p.x, p.y + 0.02, p.z);
      b.mesh.rotation.set(-Math.PI / 2, 0, 0);
      b.mesh.scale.set(0.75 * sc, 0.45 * sc, 1);
      usedF.push(b);
    }
    for (const e of fxList) {
      const fx = this.fx(world.root, fi++);
      fx.r = pool.req(e.key, e.cw, e.ch, 1, e.draw);
      fx.use(false);
      fx.mesh.visible = true;
      fx.mesh.position.set(e.x, e.y, e.z);
      fx.mesh.quaternion.copy(cam.quaternion);
      fx.mesh.scale.set(e.w, e.h, 1);
      usedF.push(fx);
    }
    for (let i = ai; i < this.actors.length; i++) this.actors[i].mesh.visible = false;
    for (let i = fi; i < this.fxs.length; i++) this.fxs[i].mesh.visible = false;
    pool.flush();
    for (const a of usedA) a.bind();
    for (const e of usedF) e.bind();

    return V(...look);
  }
}

const fwd = new THREE.Vector3();

const EpInner: React.FC<{ ep: EpId; kit: Kit; shots: EpShot[]; shot: EpShot }> = ({ ep, kit, shot }) => {
  const f = useCurrentFrame();
  const { camera, scene } = useThree();
  const world = useMemo(() => new World(kit), [kit]);
  const rig = useMemo(() => new EpisodeRig(ep, world.root), [ep, world]);
  const fx = useMemo(() => ({
    ink: new InkPass(scene, camera as THREE.PerspectiveCamera),
    lens: new LensBlur({ maxCoC: 24, nearScale: 1.2 }),
    bloom: makeBloom(),
    tone: new ToneMappingEffect({ mode: ToneMappingMode.NEUTRAL }),
    grade: new GradeEffect(GRADES.day, GRADE_STRENGTH.day),
  }), [camera, scene]);
  useEffect(() => () => fx.ink.dispose(), [fx]);

  const cam = camera as THREE.PerspectiveCamera;
  // Let base World update sky, river, town, clouds, and light presets (shot 11/12/13 = golden, others = day)
  const baseId = shot.light === "golden" ? 12 : 2;
  world.update(baseId, f, cam, scene);
  const look = rig.update(f, shot, cam, world);
  noInkFallback(world.root);

  cam.getWorldDirection(fwd);
  fx.lens.focus = Math.max(0.3, look.sub(cam.position).dot(fwd));
  fx.lens.cInf = shot.cInf;
  gradeFor(fx.grade, shot.light);

  return (
    <>
      <primitive object={world.root} dispose={null} />
      <EffectComposer multisampling={4}>
        <primitive object={fx.ink} dispose={null} />
        <primitive object={fx.lens.pre} dispose={null} />
        <primitive object={fx.lens.main} dispose={null} />
        <primitive object={fx.bloom} dispose={null} />
        <primitive object={fx.tone} dispose={null} />
        <primitive object={fx.grade} dispose={null} />
      </EffectComposer>
    </>
  );
};

const makeEpisodeComp = (ep: EpId): React.FC => {
  const total = EP_FRAMES[ep];
  const shots = makeShots(total, [SX, SY, SZ], [PX, PY, PZ]);
  const Comp: React.FC = () => {
    const f = useCurrentFrame();
    const kit = useKit();
    if (!kit) return null;
    const shot = shots.find((s) => f >= s.a && f < s.b) ?? shots[shots.length - 1];
    const flash = f >= 130 && f < 134 ? [1, 0.75, 0.45, 0.2][f - 130] : 0;
    return (
      <AbsoluteFill style={{ background: "#cfe3f2" }}>
        <ThreeCanvas width={1080} height={1920} shadows gl={{ antialias: false, stencil: false, powerPreference: "high-performance", toneMappingExposure: 1.0 }}
          camera={{ fov: 38, near: 0.2, far: 1500 }}>
          <EpInner ep={ep} kit={kit} shots={shots} shot={shot} />
        </ThreeCanvas>
        {flash > 0 && <AbsoluteFill style={{ background: "#ffffff", opacity: flash }} />}
      </AbsoluteFill>
    );
  };
  return Comp;
};

export const CavendishShort = makeEpisodeComp("cavendish");
export const MagdeburgShort = makeEpisodeComp("magdeburg");
export const FaradayShort = makeEpisodeComp("faraday");
