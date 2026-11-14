// Script-synced 15-shot cameras, bespoke 3D props, and expressive 2D character
// choreography for the 6 Cartoon 3D Physics Shorts:
//   GalileoShort, ArchimedesShort, NewtonShort, FranklinShort, TeslaShort, RontgenShort.
import * as THREE from "three";
import { NOINK } from "../bridge/ink";
import { twoTone } from "../bridge/shade";
import { Strand } from "../bridge/build";
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
} from "../bridge/toon";
import { V3, FPS, clamp01, V } from "../bridge/story";

export type NewEpId = "galileo" | "archimedes" | "newton" | "franklin" | "tesla" | "rontgen";

export type EpShot = {
  id: number;
  a: number;
  b: number;
  light: "day" | "golden";
  cInf: number;
  pos0: V3;
  look0: V3;
  pos1: V3;
  look1: V3;
  fov?: number;
  roll?: number;
  kickAt?: number;
};

export type Place = {
  key: string;
  draw: (p: Pen) => void;
  x: number;
  y: number;
  z: number;
  scale?: number;
  mirror?: boolean;
};

export type FxPlace = {
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

const SCIENTIST_OUTFIT: Outfit = {
  jacket: "#6e2c26",
  pants: "#2f2a28",
  boots: INK,
  hat: "hair",
  hair: "#4a382b",
  buttons: "#e2b857",
};
const KING_OUTFIT: Outfit = {
  jacket: "#8f2232",
  pants: "#3a2529",
  boots: INK,
  hat: "tophat",
  sash: "#f0c84b",
  buttons: "#f0c84b",
  build: "stout",
};
const ARCH_ROBE: Outfit = {
  jacket: "#e5dec9",
  pants: "#d8cfa8",
  boots: "#8a5a36",
  hat: "hair",
  hair: "#b8b0a2",
  sash: "#3b6691",
};
const GREEK_BARE: Outfit = {
  jacket: "#f5c9a0",
  pants: "#e5dec9",
  boots: INK,
  hat: "hair",
  hair: "#b8b0a2",
};
const MORGAN_OUTFIT: Outfit = {
  jacket: "#24262e",
  pants: "#1d1f26",
  boots: INK,
  hat: "tophat",
  buttons: "#f0c84b",
  moustache: "#6a6e75",
  build: "stout",
};
const DOC_OUTFIT: Outfit = {
  jacket: "#eceef2",
  pants: "#2d333b",
  boots: INK,
  hat: "hair",
  hair: "#3d332a",
  buttons: "#5b7691",
};
const BERTHA_OUTFIT: Outfit = {
  jacket: "#5b3b6e",
  pants: "#3c2a4a",
  boots: INK,
  hat: "bonnet",
  dress: "#7a4e8f",
};
const ASTRONAUT_KID: Outfit = {
  jacket: "#f2f4f8",
  pants: "#dce2eb",
  boots: "#5e6573",
  hat: "cap",
  cap: "#8ec5d6",
  build: "kid",
};

const NEWTON_OUTFIT: Outfit = {
  jacket: "#3b2c47",
  pants: "#2b2630",
  boots: INK,
  hat: "hair",
  hair: "#5a3d28",
  buttons: "#d8cfa8",
};
const FRANKLIN_OUTFIT: Outfit = {
  jacket: "#2f3d52",
  pants: "#252930",
  boots: INK,
  hat: "hair",
  hair: "#b5b2ac",
  buttons: "#d8cfa8",
  build: "stout",
};
const TESLA_OUTFIT: Outfit = {
  jacket: "#1f2533",
  pants: "#1b1e26",
  boots: INK,
  hat: "hair",
  hair: "#1e1a18",
  moustache: "#1e1a18",
  buttons: "#96a6bd",
};
const RONTGEN_OUTFIT: Outfit = {
  jacket: "#2d323b",
  pants: "#23272e",
  boots: INK,
  hat: "hair",
  hair: "#4f3e31",
  moustache: "#4f3e31",
  buttons: "#9ea6b2",
};

// Moon stage offset behind/beside Park for Galileo S14
const MX_OFF = 11.5;
const MZ_OFF = 0.5;

type Mats = {
  wood: THREE.Material;
  stone: THREE.Material;
  iron: THREE.Material;
  copper: THREE.Material;
  brass: THREE.Material;
  glass: THREE.Material;
  red: THREE.Material;
  paper: THREE.Material;
};

export interface NewEpRig {
  // Galileo
  towerGroup: THREE.Group;
  ballHeavy: THREE.Mesh;
  ballLight: THREE.Mesh;
  trailHeavy: THREE.Mesh;
  trailLight: THREE.Mesh;
  bowlBall: THREE.Mesh;
  marbleBall: THREE.Mesh;
  featherMesh: THREE.Group;
  airStreams: THREE.Mesh[];
  moonBackdrop: THREE.Mesh;
  moonEarth: THREE.Mesh;
  moonHammer: THREE.Group;
  moonFeather: THREE.Group;
  // Archimedes
  waterLvl: THREE.Mesh;
  crownMesh: THREE.Mesh;
  goldBlock: THREE.Mesh;
  silverBlock: THREE.Mesh;
  jarWaterL: THREE.Mesh;
  jarWaterR: THREE.Mesh;
  jarCubeL: THREE.Mesh;
  jarCubeR: THREE.Mesh;
  shipGroup: THREE.Group;
  // Newton
  appleMesh: THREE.Mesh;
  moonMesh: THREE.Mesh;
  orbitBallSlow: THREE.Mesh;
  orbitBallFast: THREE.Mesh;
  bucketPivot: THREE.Group;
  satGroup: THREE.Group;
  // Franklin
  kiteGroup: THREE.Group;
  kiteString: Strand;
  franklinSpark: THREE.Mesh;
  leydenJar: THREE.Mesh;
  zapBall: THREE.Mesh;
  parkZap: THREE.Mesh;
  rodBolt: THREE.Mesh;
  // Tesla
  teslaTower: THREE.Group;
  teslaArc: THREE.Mesh;
  bulbs: THREE.Mesh[];
  moneyBag: THREE.Mesh;
  forkL: THREE.Group;
  forkR: THREE.Group;
  waveRings: THREE.Mesh[];
  phoneScreen: THREE.Mesh;
  // Rontgen
  darkScreenWall: THREE.Mesh;
  xrayScreen: THREE.Mesh;
  xrayBeam: THREE.Mesh;
  bonesOverlay: THREE.Mesh;
  shoeFootBones: THREE.Mesh;
  marbles: THREE.Mesh[];
}

export function buildNewShots(ep: NewEpId, stage: V3, park: V3): EpShot[] {
  const [sx, sy, sz] = stage;
  const [px, py, pz] = park;

  // Frame boundaries aligned proportionally to each script's 15 spoken lines on a 70.0 s (2100f) timeline
  const cuts: Record<NewEpId, number[]> = {
    galileo: [0, 135, 277, 409, 568, 683, 825, 959, 1124, 1216, 1317, 1474, 1624, 1754, 1876, 2100],
    archimedes: [0, 165, 314, 442, 591, 712, 825, 971, 1118, 1214, 1333, 1489, 1624, 1777, 1893, 2100],
    newton: [0, 143, 313, 453, 564, 671, 844, 972, 1120, 1224, 1354, 1472, 1643, 1776, 1916, 2100],
    franklin: [0, 152, 316, 445, 593, 729, 878, 1000, 1123, 1237, 1377, 1533, 1660, 1802, 1926, 2100],
    tesla: [0, 181, 334, 477, 606, 750, 894, 1031, 1166, 1292, 1396, 1556, 1686, 1804, 1936, 2100],
    rontgen: [0, 160, 312, 443, 562, 679, 815, 963, 1119, 1235, 1374, 1525, 1669, 1791, 1929, 2100],
  };
  const B = cuts[ep];
  const S = (id: number, light: "day" | "golden", cInf: number, pos0: V3, look0: V3, pos1: V3, look1: V3, extra: Partial<EpShot> = {}): EpShot => ({
    id,
    a: B[id - 1],
    b: B[id],
    light,
    cInf,
    pos0,
    look0,
    pos1,
    look1,
    fov: extra.fov ?? 44,
    roll: extra.roll,
    kickAt: extra.kickAt,
  });

  if (ep === "galileo") {
    return [
      // S01: Wide Pisa tower + Galileo pondering the 2,000-year lie
      S(1, "day", 7, [sx + 0.4, sy + 2.4, sz + 9.2], [sx - 0.3, sy + 2.1, sz - 0.8], [sx + 0.1, sy + 2.2, sz + 7.8], [sx - 0.3, sy + 2.1, sz - 0.8], { fov: 46 }),
      // S02: Young rebel Galileo pointing up to the top of the tower
      S(2, "day", 9, [sx + 1.1, sy + 1.5, sz + 5.6], [sx + 0.1, sy + 1.4, sz], [sx + 0.8, sy + 2.3, sz + 6.4], [sx - 0.4, sy + 2.6, sz - 0.8]),
      // S03: Camera tilts UP to top balcony as Galileo climbs with 2 iron cannonballs
      S(3, "day", 7, [sx + 0.8, sy + 2.2, sz + 6.6], [sx - 1.0, sy + 2.8, sz - 1.3], [sx + 0.4, sy + 4.7, sz + 5.0], [sx - 1.0, sy + 4.4, sz - 1.3]),
      // S04: Tilts DOWN to angry crowd of pointing professors in plaza below tower
      S(4, "day", 8, [sx + 1.4, sy + 1.7, sz + 6.8], [sx + 0.6, sy + 1.25, sz + 0.5], [sx + 2.2, sy + 1.55, sz + 5.4], [sx + 0.9, sy + 1.2, sz + 0.6]),
      // S05: Aristotle false hypothesis: heavy drops fast vs light slow beside tower
      S(5, "day", 8, [sx + 0.1, sy + 2.7, sz + 7.5], [sx - 0.3, sy + 2.1, sz - 0.9], [sx - 0.2, sy + 2.3, sz + 6.6], [sx - 0.3, sy + 1.9, sz - 0.9]),
      // S06: Dramatic Dutch angle on scowling professors + brave Galileo high above
      S(6, "day", 8, [sx + 2.2, sy + 1.5, sz + 5.6], [sx + 0.2, sy + 1.8, sz], [sx + 1.4, sy + 2.6, sz + 6.0], [sx - 0.4, sy + 2.8, sz - 0.8], { roll: 0.055 }),
      // S07: Tight close-up AT TOP BALCONY — Galileo leaning over railing holding both spheres side by side!
      S(7, "day", 10, [sx + 0.25, sy + 5.05, sz + 3.2], [sx - 0.9, sy + 4.55, sz - 1.2], [sx - 0.05, sy + 4.95, sz + 2.3], [sx - 0.85, sy + 4.5, sz - 1.2], { fov: 40 }),
      // S08: THE DROP — camera tracks BOTH falling balls all the way down to cobblestone + boom!
      S(8, "day", 7, [sx + 0.3, sy + 4.4, sz + 5.6], [sx - 0.3, sy + 3.6, sz - 1.1], [sx + 0.4, sy + 1.45, sz + 5.2], [sx + 0.1, sy + 0.9, sz - 0.6], { kickAt: 1018 }),
      // S09: Luckily — Galileo grins triumphantly beside the twin cannonballs on ground
      S(9, "day", 10, [sx - 0.5, sy + 1.4, sz + 5.2], [sx + 0.15, sy + 1.05, sz - 0.2], [sx - 0.2, sy + 1.35, sz + 4.4], [sx + 0.15, sy + 1.05, sz - 0.2], { fov: 40 }),
      // S10: Unluckily — humiliated professors chase Galileo out of the plaza
      S(10, "day", 8, [sx + 1.6, sy + 1.6, sz + 6.4], [sx + 0.4, sy + 1.2, sz + 0.3], [sx + 2.4, sy + 1.6, sz + 6.0], [sx + 1.1, sy + 1.2, sz + 0.3]),
      // S11: Park analogy setup — bowling ball & tiny marble suspended on tall drop-frame
      S(11, "golden", 7, [px - 0.8, py + 1.8, pz - 6.8], [px, py + 1.5, pz], [px - 0.3, py + 1.65, pz - 5.6], [px, py + 1.45, pz]),
      // S12: Bowling ball & marble race neck-and-neck downward and hit grass simultaneously!
      S(12, "golden", 8, [px + 0.4, py + 1.9, pz - 6.0], [px, py + 1.35, pz], [px + 0.1, py + 1.25, pz - 5.0], [px, py + 1.0, pz], { kickAt: 1528 }),
      // S13: Feather held up by rising air flutter vs fast-dropping bowling ball
      S(13, "golden", 9, [px - 0.6, py + 1.8, pz - 5.4], [px + 0.1, py + 1.55, pz], [px - 0.2, py + 1.7, pz - 4.7], [px + 0.1, py + 1.45, pz]),
      // S14: MOON STAGE — hammer and feather fall slowly in lockstep to hit lunar dust together!
      S(14, "day", 9, [px + MX_OFF - 0.4, py + 1.85, pz + MZ_OFF - 5.6], [px + MX_OFF, py + 1.25, pz + MZ_OFF], [px + MX_OFF + 0.2, py + 1.45, pz + MZ_OFF - 4.5], [px + MX_OFF, py + 0.95, pz + MZ_OFF], { kickAt: 1835 }),
      // S15: Callback hero pose back in front of the whole Leaning Tower of Pisa!
      S(15, "day", 6, [sx - 0.4, sy + 2.0, sz + 6.8], [sx - 0.3, sy + 1.85, sz - 0.6], [sx + 0.4, sy + 2.6, sz + 9.2], [sx - 0.4, sy + 2.0, sz - 0.8], { fov: 46 }),
    ];
  }

  if (ep === "archimedes") {
    return [
      S(1, "day", 8, [sx + 0.6, sy + 1.55, sz + 6.0], [sx, sy + 1.25, sz], [sx + 0.2, sy + 1.45, sz + 5.0], [sx, sy + 1.25, sz]),
      S(2, "day", 8, [sx + 1.4, sy + 1.65, sz + 6.2], [sx + 0.2, sy + 1.25, sz], [sx + 0.9, sy + 1.5, sz + 5.2], [sx + 0.2, sy + 1.25, sz]),
      S(3, "day", 10, [sx + 1.8, sy + 1.45, sz + 4.6], [sx + 0.9, sy + 1.15, sz - 0.2], [sx + 1.2, sy + 1.38, sz + 3.8], [sx + 1.0, sy + 1.15, sz - 0.2], { fov: 38 }),
      S(4, "day", 8, [sx + 0.6, sy + 1.65, sz + 6.4], [sx + 0.4, sy + 1.25, sz], [sx - 0.1, sy + 1.55, sz + 5.6], [sx + 0.4, sy + 1.25, sz]),
      S(5, "day", 9, [sx - 0.6, sy + 1.6, sz + 5.8], [sx + 0.3, sy + 1.25, sz], [sx, sy + 1.5, sz + 4.9], [sx + 0.3, sy + 1.25, sz], { roll: -0.04 }),
      S(6, "day", 9, [sx - 0.9, sy + 1.85, sz + 5.4], [sx - 0.45, sy + 1.1, sz - 0.35], [sx - 0.6, sy + 1.55, sz + 4.4], [sx - 0.45, sy + 0.95, sz - 0.35]),
      S(7, "day", 9, [sx - 0.3, sy + 1.5, sz + 4.6], [sx - 0.45, sy + 0.85, sz - 0.35], [sx - 0.5, sy + 1.35, sz + 3.8], [sx - 0.45, sy + 0.8, sz - 0.35], { roll: 0.05 }),
      S(8, "day", 8, [sx - 0.4, sy + 1.65, sz + 5.2], [sx - 0.35, sy + 1.1, sz - 0.25], [sx + 0.1, sy + 1.85, sz + 6.2], [sx - 0.35, sy + 1.15, sz - 0.25], { kickAt: 990 }),
      S(9, "day", 10, [sx - 0.2, sy + 1.55, sz + 5.2], [sx - 0.2, sy + 1.2, sz], [sx + 0.2, sy + 1.48, sz + 4.5], [sx - 0.2, sy + 1.2, sz]),
      S(10, "day", 8, [sx + 1.2, sy + 1.6, sz + 6.4], [sx + 0.6, sy + 1.25, sz + 0.4], [sx + 2.2, sy + 1.6, sz + 6.0], [sx + 1.3, sy + 1.25, sz + 0.4]),
      S(11, "golden", 7, [px - 0.6, py + 1.7, pz - 6.2], [px, py + 1.25, pz], [px - 0.2, py + 1.55, pz - 5.2], [px, py + 1.2, pz]),
      S(12, "golden", 9, [px + 0.2, py + 1.5, pz - 5.0], [px, py + 1.1, pz], [px, py + 1.38, pz - 4.1], [px, py + 1.05, pz], { kickAt: 1525 }),
      S(13, "golden", 8, [sx + 0.5, sy + 1.6, sz + 5.6], [sx + 0.1, sy + 1.1, sz - 0.2], [sx + 0.2, sy + 1.45, sz + 4.6], [sx + 0.1, sy + 1.05, sz - 0.2]),
      S(14, "day", 8, [sx + 1.1, sy + 1.65, sz + 5.8], [sx + 0.3, sy + 1.25, sz], [sx + 0.6, sy + 1.5, sz + 5.0], [sx + 0.3, sy + 1.25, sz]),
      S(15, "day", 6, [sx - 0.4, sy + 1.85, sz + 6.4], [sx + 0.2, sy + 1.25, sz], [sx + 0.5, sy + 2.5, sz + 8.6], [sx + 0.2, sy + 1.25, sz]),
    ];
  }

  if (ep === "newton") {
    return [
      S(1, "day", 7, [sx + 0.2, sy + 1.65, sz + 7.6], [sx + 0.1, sy + 2.0, sz - 0.6], [sx - 0.1, sy + 1.9, sz + 6.6], [sx + 0.2, sy + 2.2, sz - 0.6], { fov: 48 }),
      S(2, "day", 8, [sx + 1.1, sy + 1.75, sz + 6.8], [sx + 0.1, sy + 1.3, sz], [sx + 0.6, sy + 1.6, sz + 5.6], [sx + 0.1, sy + 1.3, sz]),
      S(3, "day", 9, [sx - 0.8, sy + 1.4, sz + 5.4], [sx + 0.3, sy + 1.65, sz - 0.5], [sx - 0.4, sy + 1.65, sz + 5.8], [sx + 0.4, sy + 2.0, sz - 0.5]),
      S(4, "day", 10, [sx - 0.5, sy + 1.9, sz + 4.9], [sx - 0.15, sy + 1.2, sz - 0.4], [sx - 0.3, sy + 1.35, sz + 4.3], [sx - 0.15, sy + 0.9, sz - 0.4], { kickAt: 482 }),
      S(5, "day", 9, [sx + 1.0, sy + 1.5, sz + 5.4], [sx + 0.1, sy + 1.25, sz], [sx + 0.6, sy + 1.45, sz + 4.6], [sx + 0.1, sy + 1.25, sz]),
      S(6, "day", 8, [sx + 0.3, sy + 1.7, sz + 6.6], [sx + 0.4, sy + 1.65, sz - 0.3], [sx + 0.6, sy + 1.85, sz + 5.8], [sx + 0.6, sy + 1.7, sz - 0.3], { roll: 0.04 }),
      S(7, "day", 9, [sx + 1.25, sy + 1.95, sz + 5.2], [sx + 1.2, sy + 1.65, sz - 0.45], [sx + 1.25, sy + 1.8, sz + 4.3], [sx + 1.2, sy + 1.6, sz - 0.45], { fov: 40 }),
      S(8, "day", 8, [sx + 1.2, sy + 2.0, sz + 5.6], [sx + 1.2, sy + 1.55, sz - 0.45], [sx + 1.5, sy + 2.2, sz + 6.2], [sx + 1.2, sy + 1.55, sz - 0.45], { kickAt: 990 }),
      S(9, "day", 9, [sx + 1.0, sy + 1.7, sz + 5.4], [sx + 0.8, sy + 1.5, sz - 0.2], [sx + 0.8, sy + 1.6, sz + 4.8], [sx + 0.8, sy + 1.5, sz - 0.2]),
      S(10, "day", 9, [sx + 1.3, sy + 1.65, sz + 5.6], [sx + 0.9, sy + 1.4, sz - 0.2], [sx + 1.6, sy + 1.55, sz + 4.9], [sx + 0.9, sy + 1.3, sz - 0.2], { roll: -0.05 }),
      S(11, "golden", 7, [px - 0.7, py + 1.85, pz - 6.6], [px, py + 1.5, pz], [px - 0.2, py + 1.75, pz - 5.6], [px, py + 1.5, pz]),
      S(12, "golden", 8, [px + 0.3, py + 1.95, pz - 6.2], [px, py + 1.55, pz], [px + 0.1, py + 1.85, pz - 5.2], [px, py + 1.55, pz]),
      S(13, "golden", 8, [sx + 1.1, sy + 1.95, sz + 5.8], [sx + 1.15, sy + 1.55, sz - 0.45], [sx + 0.9, sy + 1.8, sz + 4.9], [sx + 1.15, sy + 1.55, sz - 0.45]),
      S(14, "day", 8, [sx + 0.9, sy + 1.9, sz + 6.0], [sx + 0.8, sy + 1.55, sz - 0.3], [sx + 1.1, sy + 1.75, sz + 5.2], [sx + 0.8, sy + 1.55, sz - 0.3]),
      S(15, "day", 6, [sx - 0.2, sy + 1.8, sz + 6.4], [sx + 0.4, sy + 1.5, sz], [sx + 0.5, sy + 2.4, sz + 8.4], [sx + 0.4, sy + 1.5, sz]),
    ];
  }

  if (ep === "franklin") {
    return [
      S(1, "day", 7, [sx - 0.2, sy + 2.2, sz + 8.2], [sx - 0.2, sy + 2.1, sz - 0.3], [sx + 0.1, sy + 2.4, sz + 7.2], [sx - 0.2, sy + 2.3, sz - 0.3], { fov: 48 }),
      S(2, "day", 8, [sx + 1.4, sy + 1.65, sz + 6.2], [sx + 0.3, sy + 1.3, sz], [sx + 0.9, sy + 1.55, sz + 5.2], [sx + 0.3, sy + 1.3, sz]),
      S(3, "day", 8, [sx - 0.8, sy + 2.2, sz + 7.4], [sx - 0.4, sy + 2.4, sz - 0.5], [sx - 0.4, sy + 2.6, sz + 6.4], [sx - 0.4, sy + 2.5, sz - 0.5]),
      S(4, "day", 8, [sx - 0.5, sy + 1.85, sz + 6.0], [sx - 0.3, sy + 1.7, sz - 0.2], [sx - 0.2, sy + 1.65, sz + 5.0], [sx - 0.3, sy + 1.6, sz - 0.2]),
      S(5, "day", 9, [sx + 1.1, sy + 1.55, sz + 5.4], [sx + 0.5, sy + 1.25, sz + 0.2], [sx + 0.8, sy + 1.48, sz + 4.7], [sx + 0.5, sy + 1.25, sz + 0.2]),
      S(6, "day", 9, [sx + 0.7, sy + 1.65, sz + 5.2], [sx + 0.2, sy + 1.4, sz - 0.1], [sx + 0.4, sy + 1.55, sz + 4.4], [sx + 0.1, sy + 1.4, sz - 0.1]),
      S(7, "day", 10, [sx + 0.2, sy + 1.6, sz + 4.2], [sx - 0.25, sy + 1.45, sz - 0.1], [sx - 0.1, sy + 1.52, sz + 3.4], [sx - 0.25, sy + 1.4, sz - 0.1], { roll: 0.05 }),
      S(8, "day", 10, [sx + 0.1, sy + 1.55, sz + 4.2], [sx - 0.15, sy + 1.38, sz - 0.05], [sx + 0.3, sy + 1.65, sz + 5.0], [sx - 0.15, sy + 1.38, sz - 0.05], { kickAt: 1030 }),
      S(9, "day", 9, [sx - 0.4, sy + 1.55, sz + 5.2], [sx + 0.1, sy + 1.25, sz], [sx, sy + 1.48, sz + 4.4], [sx + 0.1, sy + 1.25, sz]),
      S(10, "day", 8, [sx + 1.4, sy + 1.6, sz + 5.8], [sx + 0.7, sy + 1.2, sz + 0.3], [sx + 1.0, sy + 1.5, sz + 5.0], [sx + 0.7, sy + 1.2, sz + 0.3]),
      S(11, "golden", 7, [px - 0.7, py + 1.75, pz - 6.4], [px, py + 1.25, pz], [px - 0.2, py + 1.6, pz - 5.4], [px, py + 1.25, pz]),
      S(12, "golden", 9, [px + 0.4, py + 1.55, pz - 5.0], [px + 0.3, py + 1.25, pz], [px + 0.2, py + 1.42, pz - 4.1], [px + 0.3, py + 1.25, pz], { kickAt: 1595 }),
      S(13, "golden", 8, [sx + 0.7, sy + 2.2, sz + 6.4], [sx + 0.5, sy + 2.0, sz - 0.4], [sx + 0.4, sy + 2.0, sz + 5.4], [sx + 0.5, sy + 1.9, sz - 0.4]),
      S(14, "day", 8, [sx + 0.3, sy + 2.0, sz + 6.8], [sx + 0.2, sy + 1.7, sz - 0.3], [sx + 0.6, sy + 2.2, sz + 6.0], [sx + 0.2, sy + 1.7, sz - 0.3]),
      S(15, "day", 6, [sx - 0.3, sy + 2.0, sz + 6.8], [sx, sy + 1.7, sz], [sx + 0.5, sy + 2.7, sz + 9.0], [sx, sy + 1.8, sz]),
    ];
  }

  if (ep === "tesla") {
    return [
      S(1, "day", 7, [sx - 0.2, sy + 2.1, sz + 8.4], [sx - 0.4, sy + 2.2, sz - 0.6], [sx + 0.2, sy + 2.6, sz + 7.2], [sx - 0.4, sy + 2.4, sz - 0.6], { fov: 46 }),
      S(2, "day", 8, [sx + 1.2, sy + 1.7, sz + 6.4], [sx + 0.2, sy + 1.4, sz], [sx + 0.7, sy + 1.55, sz + 5.4], [sx + 0.2, sy + 1.4, sz]),
      S(3, "day", 9, [sx + 0.5, sy + 1.6, sz + 5.8], [sx + 0.3, sy + 1.35, sz], [sx + 0.1, sy + 1.5, sz + 4.8], [sx + 0.3, sy + 1.35, sz]),
      S(4, "day", 9, [sx - 0.6, sy + 1.65, sz + 5.6], [sx + 0.1, sy + 1.35, sz], [sx - 0.2, sy + 1.55, sz + 4.8], [sx + 0.1, sy + 1.35, sz]),
      S(5, "day", 8, [sx + 0.4, sy + 2.2, sz + 6.6], [sx, sy + 1.9, sz - 0.3], [sx, sy + 2.0, sz + 5.6], [sx, sy + 1.8, sz - 0.3]),
      S(6, "day", 8, [sx + 0.9, sy + 2.1, sz + 6.4], [sx, sy + 1.95, sz - 0.3], [sx + 0.3, sy + 1.85, sz + 5.4], [sx, sy + 1.8, sz - 0.3], { roll: 0.04 }),
      S(7, "day", 9, [sx - 0.4, sy + 1.6, sz + 5.4], [sx + 0.2, sy + 1.35, sz], [sx - 0.1, sy + 1.5, sz + 4.6], [sx + 0.2, sy + 1.35, sz]),
      S(8, "day", 9, [sx + 1.2, sy + 1.55, sz + 5.2], [sx + 0.4, sy + 1.3, sz], [sx + 1.6, sy + 1.6, sz + 5.8], [sx + 0.6, sy + 1.3, sz]),
      S(9, "day", 9, [sx + 0.9, sy + 1.65, sz + 5.2], [sx + 0.8, sy + 1.35, sz], [sx + 0.6, sy + 1.55, sz + 4.5], [sx + 0.8, sy + 1.35, sz]),
      S(10, "day", 7, [sx - 0.2, sy + 2.1, sz + 6.8], [sx - 0.7, sy + 1.8, sz - 0.7], [sx + 0.3, sy + 2.3, sz + 7.4], [sx - 0.7, sy + 1.6, sz - 0.7], { kickAt: 1320 }),
      S(11, "golden", 7, [px - 0.5, py + 1.65, pz - 6.0], [px, py + 1.15, pz], [px - 0.1, py + 1.5, pz - 5.0], [px, py + 1.15, pz]),
      S(12, "golden", 8, [px + 0.4, py + 1.55, pz - 5.2], [px, py + 1.1, pz], [px - 0.1, py + 1.42, pz - 4.4], [px, py + 1.1, pz]),
      S(13, "golden", 8, [sx + 0.4, sy + 1.85, sz + 6.0], [sx + 0.2, sy + 1.55, sz - 0.3], [sx, sy + 1.7, sz + 5.1], [sx + 0.2, sy + 1.55, sz - 0.3]),
      S(14, "day", 9, [px - 0.2, py + 1.55, pz - 4.8], [px, py + 1.15, pz], [px + 0.1, py + 1.42, pz - 4.0], [px, py + 1.15, pz]),
      S(15, "day", 6, [sx - 0.3, sy + 2.0, sz + 6.8], [sx - 0.1, sy + 1.8, sz - 0.4], [sx + 0.4, sy + 2.7, sz + 9.0], [sx - 0.1, sy + 1.8, sz - 0.4]),
    ];
  }

  // rontgen
  return [
    S(1, "day", 8, [sx + 0.5, sy + 1.65, sz + 6.4], [sx, sy + 1.35, sz - 0.3], [sx + 0.1, sy + 1.55, sz + 5.4], [sx, sy + 1.35, sz - 0.3]),
    S(2, "day", 9, [sx - 0.7, sy + 1.6, sz + 5.6], [sx - 0.6, sy + 1.3, sz - 0.3], [sx - 0.3, sy + 1.5, sz + 4.8], [sx - 0.4, sy + 1.3, sz - 0.3]),
    S(3, "day", 9, [sx + 1.0, sy + 1.6, sz + 5.2], [sx + 0.7, sy + 1.35, sz - 0.3], [sx + 1.2, sy + 1.5, sz + 4.3], [sx + 0.9, sy + 1.35, sz - 0.3]),
    S(4, "day", 9, [sx + 0.2, sy + 1.55, sz + 5.6], [sx, sy + 1.35, sz - 0.3], [sx + 0.4, sy + 1.48, sz + 4.8], [sx, sy + 1.35, sz - 0.3]),
    S(5, "day", 9, [sx + 0.5, sy + 1.55, sz + 5.0], [sx + 0.2, sy + 1.35, sz - 0.2], [sx + 0.3, sy + 1.48, sz + 4.2], [sx + 0.2, sy + 1.35, sz - 0.2]),
    S(6, "day", 10, [sx + 1.1, sy + 1.5, sz + 4.2], [sx + 0.95, sy + 1.35, sz - 0.3], [sx + 0.9, sy + 1.45, sz + 3.5], [sx + 0.95, sy + 1.35, sz - 0.3], { fov: 38 }),
    S(7, "day", 9, [sx + 0.4, sy + 1.55, sz + 5.2], [sx + 0.4, sy + 1.3, sz], [sx + 0.1, sy + 1.48, sz + 4.4], [sx + 0.4, sy + 1.3, sz]),
    S(8, "day", 10, [sx + 1.0, sy + 1.55, sz + 4.4], [sx + 0.85, sy + 1.35, sz - 0.2], [sx + 0.7, sy + 1.48, sz + 3.8], [sx + 0.85, sy + 1.35, sz - 0.2], { kickAt: 1010 }),
    S(9, "day", 9, [sx - 0.3, sy + 1.55, sz + 5.4], [sx + 0.1, sy + 1.3, sz], [sx + 0.1, sy + 1.48, sz + 4.6], [sx + 0.1, sy + 1.3, sz]),
    S(10, "day", 9, [sx + 1.1, sy + 1.45, sz + 5.2], [sx + 0.5, sy + 1.0, sz + 0.2], [sx + 0.8, sy + 1.38, sz + 4.4], [sx + 0.5, sy + 1.0, sz + 0.2]),
    S(11, "golden", 7, [px - 0.5, py + 1.65, pz - 6.0], [px, py + 1.2, pz], [px - 0.1, py + 1.5, pz - 5.0], [px, py + 1.2, pz]),
    S(12, "golden", 8, [px + 0.3, py + 1.55, pz - 5.2], [px, py + 1.15, pz], [px - 0.1, py + 1.4, pz - 4.2], [px, py + 1.15, pz], { kickAt: 1570 }),
    S(13, "golden", 9, [sx + 0.6, sy + 1.6, sz + 5.2], [sx + 0.5, sy + 1.35, sz - 0.2], [sx + 0.4, sy + 1.5, sz + 4.3], [sx + 0.5, sy + 1.35, sz - 0.2]),
    S(14, "day", 8, [sx + 0.8, sy + 1.6, sz + 5.6], [sx + 0.4, sy + 1.3, sz], [sx + 0.4, sy + 1.5, sz + 4.8], [sx + 0.4, sy + 1.3, sz]),
    S(15, "day", 6, [sx - 0.3, sy + 1.8, sz + 6.4], [sx, sy + 1.35, sz], [sx + 0.4, sy + 2.4, sz + 8.6], [sx, sy + 1.35, sz]),
  ];
}

function makeBlankRig(mats: Mats): NewEpRig {
  const mk = () => new THREE.Mesh();
  const mg = () => new THREE.Group();
  return {
    towerGroup: mg(),
    ballHeavy: mk(),
    ballLight: mk(),
    trailHeavy: mk(),
    trailLight: mk(),
    bowlBall: mk(),
    marbleBall: mk(),
    featherMesh: mg(),
    airStreams: [],
    moonBackdrop: mk(),
    moonEarth: mk(),
    moonHammer: mg(),
    moonFeather: mg(),
    waterLvl: mk(),
    crownMesh: mk(),
    goldBlock: mk(),
    silverBlock: mk(),
    jarWaterL: mk(),
    jarWaterR: mk(),
    jarCubeL: mk(),
    jarCubeR: mk(),
    shipGroup: mg(),
    appleMesh: mk(),
    moonMesh: mk(),
    orbitBallSlow: mk(),
    orbitBallFast: mk(),
    bucketPivot: mg(),
    satGroup: mg(),
    kiteGroup: mg(),
    kiteString: new Strand(12, 0.02, 0.02, mats.wood),
    franklinSpark: mk(),
    leydenJar: mk(),
    zapBall: mk(),
    parkZap: mk(),
    rodBolt: mk(),
    teslaTower: mg(),
    teslaArc: mk(),
    bulbs: [],
    moneyBag: mk(),
    forkL: mg(),
    forkR: mg(),
    waveRings: [],
    phoneScreen: mk(),
    darkScreenWall: mk(),
    xrayScreen: mk(),
    xrayBeam: mk(),
    bonesOverlay: mk(),
    shoeFootBones: mk(),
    marbles: [],
  };
}

export function buildNewEpisodeProps(
  ep: NewEpId,
  stageGroup: THREE.Group,
  analogyGroup: THREE.Group,
  mats: Mats
): NewEpRig {
  const rig = makeBlankRig(mats);
  const mGreen = twoTone(new THREE.MeshLambertMaterial({ color: "#3d7a47" }));
  const mBlue = twoTone(new THREE.MeshLambertMaterial({ color: "#3b76c4" }));
  const mGold = twoTone(new THREE.MeshPhongMaterial({ color: "#eab941", specular: "#fff3b0", shininess: 85 }), 0.2);
  const mSilver = twoTone(new THREE.MeshPhongMaterial({ color: "#c2c9d4", specular: "#ffffff", shininess: 80 }), 0.18);
  const mMoon = twoTone(new THREE.MeshLambertMaterial({ color: "#9da3ad" }));
  const mWater = twoTone(new THREE.MeshPhongMaterial({ color: "#55b8db", specular: "#ffffff", shininess: 90, transparent: true, opacity: 0.72 }), 0.15);

  if (ep === "galileo") {
    // Leaning Pisa Tower cleanly positioned left-back (-1.35, 0, -1.55) with top stone railing balcony at y=4.35
    rig.towerGroup.position.set(-1.35, 0, -1.55);
    rig.towerGroup.rotation.z = -0.075;
    for (let tier = 0; tier < 3; tier++) {
      const cyl = new THREE.Mesh(new THREE.CylinderGeometry(0.72 - tier * 0.04, 0.76 - tier * 0.04, 1.45, 20), mats.paper);
      cyl.position.y = 0.72 + tier * 1.45;
      const rim = new THREE.Mesh(new THREE.CylinderGeometry(0.8 - tier * 0.04, 0.8 - tier * 0.04, 0.12, 20), mats.stone);
      rim.position.y = 1.44 + tier * 1.45;
      rig.towerGroup.add(cyl, rim);
    }
    const railRing = new THREE.Mesh(new THREE.TorusGeometry(0.7, 0.045, 8, 20), mats.stone);
    railRing.rotation.x = Math.PI / 2;
    railRing.position.y = 4.65;
    rig.towerGroup.add(railRing);
    stageGroup.add(rig.towerGroup);

    // Cannonballs positioned CLEAR of the tower cylinder (x >= -0.35!) + speed trails
    rig.ballHeavy = new THREE.Mesh(new THREE.SphereGeometry(0.27, 20, 16), mats.iron);
    rig.ballLight = new THREE.Mesh(new THREE.SphereGeometry(0.11, 16, 12), mats.brass);
    const trailMat = new THREE.MeshBasicMaterial({ color: new THREE.Color(1.4, 1.4, 1.8), transparent: true, opacity: 0.65 });
    rig.trailHeavy = new THREE.Mesh(new THREE.CylinderGeometry(0.05, 0.22, 1.1, 10), trailMat);
    rig.trailLight = new THREE.Mesh(new THREE.CylinderGeometry(0.03, 0.09, 0.9, 10), trailMat);
    rig.trailHeavy.layers.set(NOINK);
    rig.trailLight.layers.set(NOINK);
    stageGroup.add(rig.ballHeavy, rig.ballLight, rig.trailHeavy, rig.trailLight);

    // Park analogy: wooden drop gantry + glossy bowling ball + tiny marble + fluffy white feather + air resistance streams
    for (const sx of [-1.05, 1.05]) {
      const post = new THREE.Mesh(new THREE.BoxGeometry(0.1, 2.75, 0.1), mats.wood);
      post.position.set(sx, 1.38, 0);
      analogyGroup.add(post);
    }
    const topBar = new THREE.Mesh(new THREE.BoxGeometry(2.25, 0.12, 0.14), mats.wood);
    topBar.position.set(0, 2.75, 0);
    rig.bowlBall = new THREE.Mesh(new THREE.SphereGeometry(0.24, 20, 16), mats.iron);
    rig.marbleBall = new THREE.Mesh(new THREE.SphereGeometry(0.09, 14, 10), mBlue);
    const fShaft = new THREE.Mesh(new THREE.CylinderGeometry(0.015, 0.02, 0.42, 8), mats.paper);
    const fPlume = new THREE.Mesh(new THREE.BoxGeometry(0.16, 0.34, 0.03), mats.paper);
    rig.featherMesh.add(fShaft, fPlume);
    const airMat = new THREE.MeshBasicMaterial({ color: new THREE.Color(0.9, 1.6, 2.4), transparent: true, opacity: 0.7 });
    for (let i = 0; i < 4; i++) {
      const st = new THREE.Mesh(new THREE.CylinderGeometry(0.02, 0.05, 0.35, 8), airMat);
      st.layers.set(NOINK);
      rig.airStreams.push(st);
      analogyGroup.add(st);
    }
    analogyGroup.add(topBar, rig.bowlBall, rig.marbleBall, rig.featherMesh);

    // Moon Stage (dark sky backdrop + glowing blue Earth + crater disc + silver hammer + feather)
    const spaceMat = twoTone(new THREE.MeshLambertMaterial({ color: "#121726" }));
    rig.moonBackdrop = new THREE.Mesh(new THREE.BoxGeometry(7.2, 5.2, 0.15), spaceMat);
    rig.moonBackdrop.position.set(MX_OFF, 2.5, MZ_OFF + 2.4);
    rig.moonEarth = new THREE.Mesh(new THREE.SphereGeometry(0.45, 16, 12), mBlue);
    rig.moonEarth.position.set(MX_OFF - 1.5, 3.2, MZ_OFF + 1.8);
    const moonPad = new THREE.Mesh(new THREE.CylinderGeometry(2.6, 2.8, 0.22, 24), mMoon);
    moonPad.position.set(MX_OFF, 0.11, MZ_OFF);
    for (const [cx, cz, cr] of [[-0.9, -0.4, 0.38], [0.85, 0.3, 0.28], [0.1, -1.0, 0.45]]) {
      const rim = new THREE.Mesh(new THREE.TorusGeometry(cr, 0.06, 8, 16), mats.stone);
      rim.rotation.x = Math.PI / 2;
      rim.position.set(MX_OFF + cx, 0.23, MZ_OFF + cz);
      analogyGroup.add(rim);
    }
    const hStick = new THREE.Mesh(new THREE.CylinderGeometry(0.03, 0.03, 0.45, 8), mats.wood);
    const hHead = new THREE.Mesh(new THREE.BoxGeometry(0.24, 0.1, 0.1), mSilver);
    hHead.position.y = 0.2;
    rig.moonHammer.add(hStick, hHead);
    const mfShaft = new THREE.Mesh(new THREE.CylinderGeometry(0.015, 0.02, 0.4, 8), mats.paper);
    const mfPlume = new THREE.Mesh(new THREE.BoxGeometry(0.15, 0.32, 0.03), mats.paper);
    rig.moonFeather.add(mfShaft, mfPlume);
    analogyGroup.add(rig.moonBackdrop, rig.moonEarth, moonPad, rig.moonHammer, rig.moonFeather);
  }

  if (ep === "archimedes") {
    const tub = new THREE.Mesh(new THREE.BoxGeometry(1.9, 0.76, 1.15), mats.paper);
    tub.position.set(-0.55, 0.38, -0.45);
    rig.waterLvl = new THREE.Mesh(new THREE.BoxGeometry(1.68, 0.56, 0.94), mWater);
    rig.waterLvl.position.set(-0.55, 0.42, -0.45);
    const ped = new THREE.Mesh(new THREE.CylinderGeometry(0.32, 0.38, 0.92, 12), mats.stone);
    ped.position.set(1.15, 0.46, -0.35);
    rig.crownMesh = new THREE.Mesh(new THREE.TorusGeometry(0.22, 0.075, 10, 18), mGold);
    rig.crownMesh.rotation.x = Math.PI / 2;
    rig.crownMesh.position.set(1.15, 1.02, -0.35);
    const hull = new THREE.Mesh(new THREE.BoxGeometry(1.1, 0.32, 0.48), mats.iron);
    const cabin = new THREE.Mesh(new THREE.BoxGeometry(0.36, 0.26, 0.32), mats.red);
    cabin.position.set(-0.2, 0.28, 0);
    rig.shipGroup.add(hull, cabin);
    rig.shipGroup.position.set(-0.55, 0.85, -0.45);
    stageGroup.add(tub, rig.waterLvl, ped, rig.crownMesh, rig.shipGroup);

    // Park analogy: Twin clear water jars + small dense Gold cube vs big bulky Silver block!
    const pedL = new THREE.Mesh(new THREE.CylinderGeometry(0.46, 0.46, 1.15, 16), mats.glass);
    pedL.position.set(-0.7, 0.58, 0);
    const pedR = new THREE.Mesh(new THREE.CylinderGeometry(0.46, 0.46, 1.15, 16), mats.glass);
    pedR.position.set(0.7, 0.58, 0);
    rig.jarWaterL = new THREE.Mesh(new THREE.CylinderGeometry(0.42, 0.42, 0.65, 16), mWater);
    rig.jarWaterL.position.set(-0.7, 0.34, 0);
    rig.jarWaterR = new THREE.Mesh(new THREE.CylinderGeometry(0.42, 0.42, 0.65, 16), mWater);
    rig.jarWaterR.position.set(0.7, 0.34, 0);
    rig.jarCubeL = new THREE.Mesh(new THREE.BoxGeometry(0.22, 0.22, 0.22), mGold);
    rig.jarCubeR = new THREE.Mesh(new THREE.BoxGeometry(0.44, 0.44, 0.44), mSilver);
    rig.goldBlock = rig.jarCubeL;
    rig.silverBlock = rig.jarCubeR;
    analogyGroup.add(pedL, pedR, rig.jarWaterL, rig.jarWaterR, rig.jarCubeL, rig.jarCubeR);
  }

  if (ep === "newton") {
    const trunk = new THREE.Mesh(new THREE.CylinderGeometry(0.22, 0.3, 2.5, 12), mats.wood);
    trunk.position.set(-0.95, 1.25, -1.05);
    const canopy = new THREE.Mesh(new THREE.SphereGeometry(1.4, 16, 12), mGreen);
    canopy.position.set(-0.95, 2.95, -1.05);
    rig.appleMesh = new THREE.Mesh(new THREE.SphereGeometry(0.14, 14, 10), mats.red);

    // Miniature Earth globe + mountain peak + cannonballs + GPS satellite + Moon
    const earth = new THREE.Mesh(new THREE.SphereGeometry(0.55, 20, 16), mBlue);
    earth.position.set(1.2, 1.55, -0.55);
    const mtn = new THREE.Mesh(new THREE.ConeGeometry(0.16, 0.32, 8), mats.stone);
    mtn.position.set(1.2, 2.18, -0.55);
    rig.moonMesh = new THREE.Mesh(new THREE.SphereGeometry(0.16, 14, 10), mSilver);
    rig.orbitBallSlow = new THREE.Mesh(new THREE.SphereGeometry(0.08, 10, 8), mats.iron);
    rig.orbitBallFast = new THREE.Mesh(new THREE.SphereGeometry(0.08, 10, 8), mGold);
    const satBody = new THREE.Mesh(new THREE.BoxGeometry(0.12, 0.1, 0.12), mGold);
    const wing = new THREE.Mesh(new THREE.BoxGeometry(0.42, 0.02, 0.12), mBlue);
    rig.satGroup.add(satBody, wing);
    stageGroup.add(trunk, canopy, rig.appleMesh, earth, mtn, rig.moonMesh, rig.orbitBallSlow, rig.orbitBallFast, rig.satGroup);

    // Park analogy: overhead spinning copper water bucket on taut rope!
    const rope = new THREE.Mesh(new THREE.CylinderGeometry(0.025, 0.025, 1.15, 8), mats.wood);
    rope.position.set(0, 0.58, 0);
    const bucket = new THREE.Mesh(new THREE.CylinderGeometry(0.28, 0.22, 0.42, 14), mats.copper);
    bucket.position.set(0, 1.18, 0);
    rig.bucketPivot.add(rope, bucket);
    rig.bucketPivot.position.set(0, 1.45, 0);
    analogyGroup.add(rig.bucketPivot);
  }

  if (ep === "franklin") {
    const shedRoof = new THREE.Mesh(new THREE.BoxGeometry(1.9, 0.12, 1.6), mats.wood);
    shedRoof.position.set(0.65, 2.45, -0.35);
    for (const px of [-0.2, 1.5]) {
      const post = new THREE.Mesh(new THREE.BoxGeometry(0.11, 2.4, 0.11), mats.wood);
      post.position.set(px, 1.2, -0.95);
      stageGroup.add(post);
    }
    const kiteBody = new THREE.Mesh(new THREE.BoxGeometry(0.68, 0.88, 0.06), mats.red);
    kiteBody.rotation.z = Math.PI / 4;
    rig.kiteGroup.add(kiteBody);
    rig.kiteGroup.position.set(-1.15, 3.65, -0.65);

    const key = new THREE.Mesh(new THREE.CylinderGeometry(0.05, 0.05, 0.36, 10), mats.brass);
    key.rotation.z = Math.PI / 2;
    key.position.set(-0.22, 1.38, -0.1);
    const sparkMat = new THREE.MeshBasicMaterial({ color: new THREE.Color(2.2, 3.4, 7.0) });
    rig.franklinSpark = new THREE.Mesh(new THREE.SphereGeometry(0.18, 12, 10), sparkMat);
    rig.franklinSpark.position.set(-0.04, 1.38, -0.1);
    rig.franklinSpark.layers.set(NOINK);

    rig.leydenJar = new THREE.Mesh(new THREE.CylinderGeometry(0.14, 0.14, 0.34, 14), mats.glass);
    rig.leydenJar.position.set(0.55, 1.25, 0.1);
    rig.zapBall = new THREE.Mesh(new THREE.SphereGeometry(0.28, 12, 10), sparkMat);
    rig.zapBall.position.set(0.85, 1.35, 0.2);
    rig.zapBall.layers.set(NOINK);

    const rod = new THREE.Mesh(new THREE.CylinderGeometry(0.025, 0.05, 1.3, 8), mats.iron);
    rod.position.set(0.65, 3.1, -0.35);
    rig.rodBolt = new THREE.Mesh(new THREE.CylinderGeometry(0.04, 0.04, 1.4, 8), sparkMat);
    rig.rodBolt.position.set(0.65, 4.1, -0.35);
    rig.rodBolt.layers.set(NOINK);

    stageGroup.add(shedRoof, rig.kiteGroup, rig.kiteString.mesh, key, rig.franklinSpark, rig.leydenJar, rig.zapBall, rod, rig.rodBolt);

    // Park analogy: bright red carpet + shiny brass doorknob post + static shock spark!
    const rug = new THREE.Mesh(new THREE.BoxGeometry(2.5, 0.08, 1.6), mats.red);
    rug.position.set(0, 0.04, 0);
    const door = new THREE.Mesh(new THREE.BoxGeometry(0.75, 2.0, 0.12), mats.wood);
    door.position.set(0.95, 1.0, 0);
    const knob = new THREE.Mesh(new THREE.SphereGeometry(0.11, 12, 10), mats.brass);
    knob.position.set(0.58, 1.05, -0.05);
    rig.parkZap = new THREE.Mesh(new THREE.SphereGeometry(0.16, 12, 10), sparkMat);
    rig.parkZap.position.set(0.45, 1.05, -0.05);
    rig.parkZap.layers.set(NOINK);
    analogyGroup.add(rug, door, knob, rig.parkZap);
  }

  if (ep === "tesla") {
    const leg = new THREE.Mesh(new THREE.CylinderGeometry(0.18, 0.5, 2.8, 14), mats.wood);
    leg.position.set(0, 1.4, 0);
    const dome = new THREE.Mesh(new THREE.SphereGeometry(0.58, 18, 14), mats.copper);
    dome.position.set(0, 2.95, 0);
    const arcMat = new THREE.MeshBasicMaterial({ color: new THREE.Color(2.0, 3.2, 7.2) });
    rig.teslaArc = new THREE.Mesh(new THREE.TorusGeometry(0.78, 0.05, 8, 24), arcMat);
    rig.teslaArc.rotation.x = Math.PI / 2;
    rig.teslaArc.position.set(0, 2.95, 0);
    rig.teslaArc.layers.set(NOINK);
    rig.teslaTower.add(leg, dome, rig.teslaArc);
    rig.teslaTower.position.set(-0.95, 0, -0.95);

    const bulbMat = new THREE.MeshBasicMaterial({ color: new THREE.Color(3.6, 3.1, 1.2) });
    for (const bx of [0.55, 1.15, 1.75]) {
      const stand = new THREE.Mesh(new THREE.CylinderGeometry(0.04, 0.12, 1.1, 10), mats.brass);
      stand.position.set(bx, 0.55, -0.2);
      const b = new THREE.Mesh(new THREE.SphereGeometry(0.2, 14, 12), bulbMat);
      b.position.set(bx, 1.22, -0.2);
      b.layers.set(NOINK);
      rig.bulbs.push(b);
      stageGroup.add(stand, b);
    }
    rig.moneyBag = new THREE.Mesh(new THREE.SphereGeometry(0.22, 12, 10), mGold);
    rig.moneyBag.position.set(0.35, 1.15, 0.4);
    stageGroup.add(rig.teslaTower, rig.moneyBag);

    // Park analogy: Twin tall gleaming brass tuning forks + resonance wave rings + wireless charging phone
    const mkFork = (x: number) => {
      const g = new THREE.Group();
      const stem = new THREE.Mesh(new THREE.BoxGeometry(0.1, 0.65, 0.1), mats.brass);
      stem.position.y = 0.35;
      const base = new THREE.Mesh(new THREE.BoxGeometry(0.38, 0.1, 0.1), mats.brass);
      base.position.y = 0.68;
      const t1 = new THREE.Mesh(new THREE.BoxGeometry(0.08, 0.9, 0.08), mats.brass);
      t1.position.set(-0.15, 1.12, 0);
      const t2 = new THREE.Mesh(new THREE.BoxGeometry(0.08, 0.9, 0.08), mats.brass);
      t2.position.set(0.15, 1.12, 0);
      g.add(stem, base, t1, t2);
      g.position.set(x, 0, 0);
      return g;
    };
    rig.forkL = mkFork(-0.95);
    rig.forkR = mkFork(0.95);
    analogyGroup.add(rig.forkL, rig.forkR);
    for (let i = 0; i < 3; i++) {
      const ring = new THREE.Mesh(new THREE.TorusGeometry(0.22, 0.025, 8, 18), bulbMat);
      ring.rotation.y = Math.PI / 2;
      ring.layers.set(NOINK);
      rig.waveRings.push(ring);
      analogyGroup.add(ring);
    }
    const pad = new THREE.Mesh(new THREE.CylinderGeometry(0.45, 0.45, 0.08, 16), mats.iron);
    pad.position.set(0, 0.04, -0.5);
    rig.phoneScreen = new THREE.Mesh(new THREE.BoxGeometry(0.35, 0.05, 0.6), bulbMat);
    rig.phoneScreen.position.set(0, 0.11, -0.5);
    rig.phoneScreen.layers.set(NOINK);
    analogyGroup.add(pad, rig.phoneScreen);
  }

  if (ep === "rontgen") {
    const darkMat = twoTone(new THREE.MeshLambertMaterial({ color: "#151822" }));
    rig.darkScreenWall = new THREE.Mesh(new THREE.BoxGeometry(6.5, 4.5, 0.15), darkMat);
    rig.darkScreenWall.position.set(0, 2.2, -1.8);

    const box = new THREE.Mesh(new THREE.BoxGeometry(0.95, 0.65, 0.65), mats.iron);
    box.position.set(-1.15, 1.35, -0.45);
    const table = new THREE.Mesh(new THREE.BoxGeometry(1.15, 0.95, 0.8), mats.wood);
    table.position.set(-1.15, 0.48, -0.45);

    const scrMat = new THREE.MeshBasicMaterial({ color: new THREE.Color(0.8, 3.3, 1.2) });
    rig.xrayScreen = new THREE.Mesh(new THREE.BoxGeometry(0.12, 1.25, 1.0), scrMat);
    rig.xrayScreen.position.set(1.1, 1.35, -0.35);
    rig.xrayScreen.layers.set(NOINK);

    const boneMat = new THREE.MeshBasicMaterial({ color: new THREE.Color(0.08, 0.25, 0.12) });
    rig.bonesOverlay = new THREE.Mesh(new THREE.BoxGeometry(0.14, 0.65, 0.45), boneMat);
    rig.bonesOverlay.position.set(1.08, 1.35, -0.35);
    rig.bonesOverlay.layers.set(NOINK);

    const beamMat = new THREE.MeshBasicMaterial({ color: new THREE.Color(0.4, 2.0, 0.9) });
    rig.xrayBeam = new THREE.Mesh(new THREE.CylinderGeometry(0.06, 0.26, 1.85, 12), beamMat);
    rig.xrayBeam.rotation.z = Math.PI / 2;
    rig.xrayBeam.position.set(0.0, 1.35, -0.4);
    rig.xrayBeam.layers.set(NOINK);

    const shoeBox = new THREE.Mesh(new THREE.BoxGeometry(0.8, 0.65, 0.7), mats.wood);
    shoeBox.position.set(0.4, 0.33, 0.3);
    rig.shoeFootBones = new THREE.Mesh(new THREE.BoxGeometry(0.55, 0.08, 0.45), scrMat);
    rig.shoeFootBones.position.set(0.4, 0.67, 0.3);
    rig.shoeFootBones.layers.set(NOINK);

    stageGroup.add(rig.darkScreenWall, box, table, rig.xrayScreen, rig.bonesOverlay, rig.xrayBeam, shoeBox, rig.shoeFootBones);

    // Park analogy: Chain-link wire fence + thick vertical steel posts + bouncing vs flying marbles!
    for (const px of [-0.95, 0, 0.95]) {
      const post = new THREE.Mesh(new THREE.CylinderGeometry(0.09, 0.09, 1.65, 10), mats.iron);
      post.position.set(px, 0.82, 0);
      analogyGroup.add(post);
    }
    for (let ry = 0.3; ry <= 1.5; ry += 0.3) {
      const wire = new THREE.Mesh(new THREE.BoxGeometry(2.1, 0.02, 0.02), mats.iron);
      wire.position.set(0, ry, 0);
      analogyGroup.add(wire);
    }
    for (let i = 0; i < 6; i++) {
      const m = new THREE.Mesh(new THREE.SphereGeometry(0.08, 10, 8), i % 2 ? mats.red : mBlue);
      rig.marbles.push(m);
      analogyGroup.add(m);
    }
  }

  return rig;
}

export function updateNewEpisode(
  ep: NewEpId,
  rig: NewEpRig,
  f: number,
  shot: EpShot,
  stageCenter: V3,
  parkCenter: V3,
  places: Place[],
  fxList: FxPlace[]
): void {
  const [SX, SY, SZ] = stageCenter;
  const [PX, PY, PZ] = parkCenter;
  const t = f / FPS;
  const blink = (seed: number) => ((f + seed * 19) % 58) < 4;
  const pose = Math.floor(t * 8) % 8;

  if (ep === "galileo") {
    const onBalcony = shot.id === 3 || shot.id === 7;
    const isDrop = shot.id === 8;
    const dropU = isDrop ? clamp01((f - 975) / 42) ** 2 : shot.id > 8 && shot.id <= 10 || shot.id === 15 ? 1 : 0;
    const ballY = onBalcony ? 4.55 : shot.id >= 4 && shot.id <= 6 ? 4.45 : 4.5 - dropU * 4.25;

    // Position balls CLEAR to the right of the tower rim (-0.35 & +0.25) + vertical motion streaks when dropping
    rig.ballHeavy.position.set(-0.28, ballY, -1.05);
    rig.ballLight.position.set(0.28, ballY, -1.05);
    const showTrail = isDrop && dropU > 0.05 && dropU < 0.98;
    rig.trailHeavy.visible = showTrail;
    rig.trailLight.visible = showTrail;
    rig.trailHeavy.position.set(-0.28, ballY + 0.65, -1.05);
    rig.trailLight.position.set(0.28, ballY + 0.55, -1.05);

    if (shot.id === 5) {
      const u5 = ((f - shot.a) % 60) / 60;
      rig.ballHeavy.position.set(-0.28, 4.1 - u5 * u5 * 3.7, -0.8);
      rig.ballLight.position.set(0.28, 4.1 - u5 * 0.7, -0.8);
    }

    if (isDrop && f >= 1015 && f < 1055) {
      fxList.push({
        key: "galBoom",
        cw: 260,
        ch: 260,
        draw: (p) => fxBurst(p, 0.55),
        x: SX,
        y: SY + 0.45,
        z: SZ - 0.85,
        w: 1.8,
        h: 1.4,
      });
    }

    // Galileo hero: climbs onto TOP balcony during S03/S07, sprints ahead during S10 chase, beams proudly S09/S15
    const climbY = shot.id === 3 ? clamp01((f - shot.a) / 55) * 4.48 : onBalcony ? 4.48 : 0;
    const chaseU = shot.id === 10 ? clamp01((f - shot.a) / 85) : 0;
    const chaseX = shot.id === 10 ? -0.4 + chaseU * 3.4 : 0;
    const galExpr: Expr = shot.id === 9 || shot.id === 15 ? "grin" : shot.id === 10 ? "nervous" : shot.id >= 6 && shot.id <= 7 ? "stern" : "smile";
    places.push({
      key: `gal|${shot.id === 10 ? "run" : "st"}|${galExpr}|${pose}|${blink(1) ? 1 : 0}`,
      draw: (p) =>
        shot.id === 10
          ? bodySide(p, SCIENTIST_OUTFIT, { mode: "march", phase: (t * 3.2) % 1, expr: "nervous", blink: blink(1) })
          : bodyFront(p, SCIENTIST_OUTFIT, {
              mode: "stand",
              expr: galExpr,
              blink: blink(1),
              wave: shot.id === 7 ? 0.9 : shot.id === 2 || shot.id === 15 ? 0.65 : 0.25 + 0.15 * Math.sin(t * 3),
              headTilt: 0.06 * Math.sin(t * 2.2),
            }),
      x: onBalcony || shot.id === 3 ? SX - 1.02 : SX + 0.55 + chaseX,
      y: SY + climbY,
      z: onBalcony || shot.id === 3 ? SZ - 1.12 : SZ + 0.35,
    });

    // Crowd of angry professors: ACTUALLY RUN IN during S04 ("gathered below"), recoil at S08 impact, and SPRINT-CHASE in S10!
    const gatherU = shot.id === 4 ? clamp01((f - shot.a) / 65) : 1;
    for (let i = 0; i < 4; i++) {
      const pExpr: Expr = isDrop && f >= 1015 ? "shock" : shot.id === 9 ? "dazed" : "stern";
      const baseDestX = SX + 0.7 + i * 0.52;
      const runIn = shot.id === 4 && gatherU < 0.96;
      const sprint = shot.id === 10;
      const profX = runIn
        ? baseDestX + (1 - gatherU) * (2.6 + i * 0.45)
        : sprint
          ? baseDestX - 2.3 + chaseU * 3.5
          : baseDestX + (isDrop && f >= 1018 ? 0.35 : 0);
      places.push({
        key: `prof|${i}|${runIn ? "in" : sprint ? "ch" : "st"}|${pExpr}|${pose}|${blink(i + 3) ? 1 : 0}`,
        draw: (p) =>
          runIn || sprint
            ? bodySide(p, townsfolk(i), { mode: "march", phase: (t * 3.0 + i * 0.22) % 1, expr: pExpr, blink: blink(i + 3) })
            : bodyFront(p, townsfolk(i), {
                mode: "stand",
                expr: pExpr,
                blink: blink(i + 3),
                wave: shot.id === 4 || shot.id === 6 ? 0.7 : undefined,
              }),
        x: profX,
        y: SY + (isDrop && f >= 1015 && f < 1045 ? 0.2 * Math.abs(Math.sin(t * 11 + i)) : 0),
        z: SZ + 0.8 + (i % 2) * 0.24,
        mirror: runIn,
      });
    }
    if (shot.id === 10 && f % 6 < 3) {
      fxList.push({
        key: `chaseDust|${f % 2}`,
        cw: 200,
        ch: 200,
        draw: (p) => fxBurst(p, 0.35),
        x: SX + 0.2 + chaseU * 3.2,
        y: SY + 0.28,
        z: SZ + 0.7,
        w: 0.9,
        h: 0.7,
      });
    }

    // Park Bowling Ball vs Marble vs Feather + visible air-resistance updraft streams (Shots 11-13)
    const raceU = shot.id === 12 ? clamp01((f - shot.a - 12) / 48) ** 2 : shot.id > 12 ? 1 : 0;
    const parkBallY = 2.4 - raceU * 2.15;
    rig.bowlBall.position.set(-0.55, parkBallY, 0);
    rig.marbleBall.position.set(0.05, parkBallY, 0);
    const fDropU = shot.id === 13 ? clamp01((f - shot.a) / 95) : shot.id > 13 ? 1 : 0;
    rig.featherMesh.position.set(0.55 + Math.sin(t * 4.5) * 0.24, 2.4 - fDropU * 1.65, 0);
    rig.featherMesh.rotation.z = 0.38 * Math.sin(t * 4.5);
    rig.airStreams.forEach((st, idx) => {
      st.visible = shot.id === 13;
      const au = ((t * 1.9 + idx * 0.25) % 1);
      st.position.set(0.45 + (idx - 1.5) * 0.14, 0.35 + au * 1.6, 0.1);
    });
    if (shot.id === 12 && raceU >= 0.95) {
      fxList.push({
        key: "pkRaceBoom",
        cw: 220,
        ch: 220,
        draw: (p) => fxBurst(p, 0.4),
        x: PX - 0.25,
        y: PY + 0.35,
        z: PZ + 0.1,
        w: 1.2,
        h: 0.9,
      });
    }

    if (shot.id >= 11 && shot.id <= 13) {
      places.push({
        key: `pkPar|${pose}|${blink(5) ? 1 : 0}`,
        draw: (p) => bodyFront(p, PARENT, { mode: "stand", expr: "grin", blink: blink(5), wave: 0.55 }),
        x: PX - 1.45,
        y: PY,
        z: PZ + 0.15,
      });
      places.push({
        key: `pkKid|${shot.id}|${pose}|${blink(6) ? 1 : 0}`,
        draw: (p) => bodyFront(p, KID, { mode: "stand", expr: shot.id === 12 ? "shock" : "smile", blink: blink(6) }),
        x: PX + 1.45,
        y: PY,
        z: PZ + 0.15,
        scale: 0.84,
      });
    }

    // Moon Crater Stage (Shot 14): Hammer & Feather drop in 1/6g lockstep!
    rig.moonBackdrop.visible = shot.id === 14;
    rig.moonEarth.visible = shot.id === 14;
    const moonU = shot.id === 14 ? clamp01((f - shot.a - 15) / 68) ** 2 : 0;
    const moonY = 2.15 - moonU * 1.78;
    rig.moonHammer.position.set(MX_OFF - 0.35, moonY, MZ_OFF);
    rig.moonFeather.position.set(MX_OFF + 0.35, moonY, MZ_OFF);
    if (shot.id === 14) {
      if (f >= 1835 && f < 1875) {
        fxList.push({
          key: "moonDust",
          cw: 240,
          ch: 240,
          draw: (p) => fxBurst(p, 0.45),
          x: PX + MX_OFF,
          y: PY + 0.45,
          z: PZ + MZ_OFF + 0.2,
          w: 1.7,
          h: 1.2,
        });
      }
      places.push({
        key: `astro|${pose}|${blink(8) ? 1 : 0}`,
        draw: (p) => bodyFront(p, ASTRONAUT_KID, { mode: "stand", expr: "grin", blink: blink(8), wave: 0.75 }),
        x: PX + MX_OFF + 1.15,
        y: PY + 0.22 + 0.08 * Math.abs(Math.sin(t * 2.5)),
        z: PZ + MZ_OFF + 0.2,
        scale: 0.9,
      });
    }
    return;
  }

  if (ep === "archimedes") {
    const inTub = shot.id >= 6 && shot.id <= 8;
    const dunked = shot.id >= 13;
    const sinkU = shot.id === 6 ? clamp01((f - shot.a) / 45) : shot.id === 7 ? 1 : shot.id === 8 ? 1 - clamp01((f - 990) / 18) : 0;

    rig.crownMesh.position.set(dunked ? -0.55 : 1.15, dunked ? 0.55 : 1.02, dunked ? -0.45 : -0.35);
    rig.waterLvl.scale.y = 1 + (inTub ? sinkU * 0.28 : dunked ? 0.22 : 0);
    rig.shipGroup.visible = shot.id === 15;
    rig.shipGroup.position.set(-0.55 + (shot.id === 15 ? 0.1 * Math.sin(t * 2) : 0), 0.82 + 0.04 * Math.sin(t * 3), -0.45);

    if ((shot.id === 7 || shot.id === 8) && f >= 900 && f < 1050) {
      fxList.push({
        key: `archSp|${f % 4}`,
        cw: 260,
        ch: 260,
        draw: (p) => fxSplash(p, ((f - 900) % 45) / 45),
        x: SX - 0.55,
        y: SY + 0.95,
        z: SZ - 0.35,
        w: 1.7,
        h: 1.4,
      });
    }

    const sprint = shot.id === 10 ? clamp01((f - shot.a) / 70) * 1.8 : 0;
    const archOutfit = shot.id === 8 || shot.id === 10 ? GREEK_BARE : ARCH_ROBE;
    const archExpr: Expr = shot.id === 8 ? "laugh" : shot.id >= 3 && shot.id <= 5 ? "nervous" : "grin";
    places.push({
      key: `arch|${archOutfit === GREEK_BARE ? "n" : "r"}|${archExpr}|${pose}|${blink(1) ? 1 : 0}`,
      draw: (p) =>
        shot.id === 10
          ? bodySide(p, archOutfit, { mode: "march", expr: "shock", phase: (t * 2.8) % 1, blink: blink(1) })
          : bodyFront(p, archOutfit, { mode: "stand", expr: archExpr, blink: blink(1), wave: shot.id === 8 ? 0.9 : 0.4 }),
      x: inTub ? SX - 0.55 : SX + 0.35 + sprint,
      y: SY + (inTub ? 0.55 - sinkU * 0.45 + (shot.id === 8 && f >= 990 ? 0.55 * (1 - sinkU) : 0) : 0),
      z: inTub ? SZ - 0.45 : SZ + 0.45,
    });

    // King Hiero & cheating goldsmith / guards
    if (shot.id <= 5 || shot.id >= 13) {
      places.push({
        key: `king|${pose}|${blink(2) ? 1 : 0}`,
        draw: (p) => bodyFront(p, KING_OUTFIT, { mode: "stand", expr: shot.id >= 14 ? "stern" : "stern", blink: blink(2), wave: shot.id === 1 ? 0.6 : undefined }),
        x: SX + 1.55,
        y: SY,
        z: SZ + 0.35,
      });
    }
    if (shot.id === 10 || shot.id === 14) {
      for (let i = 0; i < 2; i++) {
        places.push({
          key: `archAud|${i}|${pose}|${blink(i + 4) ? 1 : 0}`,
          draw: (p) => bodyFront(p, townsfolk(i), { mode: "stand", expr: "shock", blink: blink(i + 4) }),
          x: SX - 0.9 + i * 2.2,
          y: SY,
          z: SZ + 1.0,
        });
      }
    }

    // Twin Water Jars Analogy (S11-S12): Silver cube raises water level visibly higher than Gold cube!
    const jarDrop = shot.id === 12 ? clamp01((f - shot.a - 10) / 40) : shot.id > 12 ? 1 : 0;
    rig.jarCubeL.position.set(-0.7, 1.45 - jarDrop * 1.15, 0);
    rig.jarCubeR.position.set(0.7, 1.45 - jarDrop * 1.15, 0);
    rig.jarWaterL.scale.y = 1 + jarDrop * 0.12;
    rig.jarWaterR.scale.y = 1 + jarDrop * 0.52;
    if (shot.id === 11 || shot.id === 12) {
      places.push({
        key: `arPar|${pose}`,
        draw: (p) => bodyFront(p, PARENT, { mode: "stand", expr: "grin", wave: 0.4 }),
        x: PX - 1.4,
        y: PY,
        z: PZ + 0.2,
      });
      places.push({
        key: `arKid|${pose}`,
        draw: (p) => bodyFront(p, KID, { mode: "stand", expr: shot.id === 12 ? "shock" : "smile" }),
        x: PX + 1.4,
        y: PY,
        z: PZ + 0.2,
        scale: 0.84,
      });
    }
    return;
  }

  if (ep === "newton") {
    const bonkU = shot.id >= 4 ? clamp01((f - 462) / 22) ** 2 : 0;
    rig.appleMesh.position.set(-0.25, 2.35 - bonkU * 2.15, -0.8);
    if (shot.id === 4 && f >= 480 && f < 515) {
      fxList.push({
        key: "newBonk",
        cw: 220,
        ch: 220,
        draw: (p) => fxBurst(p, 0.5),
        x: SX - 0.25,
        y: SY + 0.35,
        z: SZ - 0.7,
        w: 1.1,
        h: 1.1,
      });
    }

    // Moon + Orbiting cannonball physics around Earth at (1.2, 1.55, -0.55)
    const moonDrop = shot.id === 10 ? clamp01((f - shot.a) / 65) ** 2 * 0.55 : 0;
    const angM = t * 1.6;
    rig.moonMesh.position.set(1.2 + Math.cos(angM) * (0.95 - moonDrop), 1.55 + Math.sin(angM) * 0.38, -0.55 + Math.sin(angM) * 0.72);
    const orbU = clamp01((f - 975) / 70);
    rig.orbitBallSlow.position.set(1.2 + orbU * 0.45, 2.28 - orbU * orbU * 0.8, -0.55);
    const fAng = Math.PI / 2 - t * 3.0;
    rig.orbitBallFast.position.set(1.2 + Math.cos(fAng) * 0.82, 1.55 + Math.sin(fAng) * 0.82, -0.55);
    const sAng = t * 2.4;
    rig.satGroup.position.set(1.2 + Math.cos(sAng) * 0.74, 1.55 + Math.sin(sAng) * 0.74, -0.55);
    rig.satGroup.rotation.z = sAng;

    const newtExpr: Expr = shot.id === 4 ? "shock" : shot.id >= 6 ? "grin" : "neutral";
    places.push({
      key: `newt|${newtExpr}|${pose}|${blink(1) ? 1 : 0}`,
      draw: (p) =>
        bodyFront(p, NEWTON_OUTFIT, {
          mode: "stand",
          expr: newtExpr,
          blink: blink(1),
          wave: shot.id >= 6 ? 0.6 : 0.25,
          headTilt: shot.id <= 3 ? 0.14 : 0.05 * Math.sin(t * 2),
        }),
      x: SX - 0.1,
      y: SY,
      z: SZ - 0.15,
    });

    if (shot.id <= 3 || shot.id === 10) {
      const scurry = ((f - shot.a) / 90);
      for (let i = 0; i < 3; i++) {
        const xRun = shot.id === 10
          ? SX + 0.6 + i * 0.55 + clamp01(scurry) * 2.4
          : SX + 2.6 - clamp01(scurry) * (1.8 + i * 0.3) + i * 0.55;
        places.push({
          key: `newAud|${i}|${pose}`,
          draw: (p) => bodySide(p, townsfolk(i + 2), { mode: "march", expr: shot.id === 10 ? "shock" : "nervous", phase: (t * 2.6 + i * 0.3) % 1 }),
          x: xRun,
          y: SY + (shot.id === 10 && f % 6 < 3 ? 0.08 : 0),
          z: SZ + 0.8 + (i % 2) * 0.25,
          mirror: shot.id <= 3,
        });
      }
    }

    // Park overhead spinning rope & copper water bucket + orbiting splash droplets
    rig.bucketPivot.rotation.z = t * 5.2;
    if (shot.id >= 11 && shot.id <= 13) {
      const ang = t * 5.2;
      fxList.push({
        key: `nwDrop|${f % 3}`,
        cw: 180,
        ch: 180,
        draw: (p) => fxStars(p, (f % 10) / 10),
        x: PX - Math.sin(ang) * 1.15,
        y: PY + 1.45 + Math.cos(ang) * 1.15,
        z: PZ + 0.05,
        w: 0.7,
        h: 0.7,
      });
      places.push({
        key: `nwKid|${pose}`,
        draw: (p) => bodyFront(p, KID, { mode: "stand", expr: "grin", wave: 0.7 }),
        x: PX,
        y: PY,
        z: PZ + 0.2,
        scale: 0.86,
      });
      places.push({
        key: `nwPar|${pose}`,
        draw: (p) => bodyFront(p, PARENT, { mode: "stand", expr: "smile", wave: 0.35 }),
        x: PX - 1.25,
        y: PY,
        z: PZ + 0.2,
      });
    }
    return;
  }

  if (ep === "franklin") {
    rig.kiteGroup.position.y = 3.6 + 0.24 * Math.sin(t * 3.0);
    rig.kiteGroup.rotation.z = 0.15 * Math.sin(t * 2.4);
    rig.kiteString.set(
      Array.from({ length: 12 }, (_, i) => {
        const u = i / 11;
        return V(-1.15 + u * 0.95, 3.6 + 0.24 * Math.sin(t * 3.0) - u * 2.22, -0.65 + u * 0.55);
      })
    );
    const keySpark = shot.id === 8 || shot.id === 1;
    rig.franklinSpark.visible = keySpark && f % 3 !== 0;
    rig.zapBall.visible = shot.id === 10 && f % 2 === 0;
    rig.leydenJar.visible = shot.id === 9;
    rig.rodBolt.visible = (shot.id >= 13 && shot.id <= 15) && f % 4 === 0;

    if (keySpark) {
      fxList.push({
        key: `fkZap|${f % 3}`,
        cw: 240,
        ch: 240,
        draw: (p) => fxStars(p, (f % 10) / 10),
        x: SX - 0.04,
        y: SY + 1.38,
        z: SZ + 0.05,
        w: 1.0,
        h: 1.0,
      });
    }
    if (shot.id === 10 && f < 1300) {
      fxList.push({
        key: "fkBoom",
        cw: 240,
        ch: 240,
        draw: (p) => fxBurst(p, 0.5),
        x: SX + 0.85,
        y: SY + 1.35,
        z: SZ + 0.25,
        w: 1.3,
        h: 1.3,
      });
    }

    const fkExpr: Expr = shot.id === 8 ? "shock" : shot.id >= 9 ? "grin" : "smile";
    const fkWalkIn = shot.id === 1 ? clamp01((f - shot.a) / 70) : 1;
    places.push({
      key: `fk|${shot.id === 1 && fkWalkIn < 0.95 ? "w" : "s"}|${fkExpr}|${pose}|${blink(1) ? 1 : 0}`,
      draw: (p) =>
        shot.id === 1 && fkWalkIn < 0.95
          ? bodySide(p, FRANKLIN_OUTFIT, { mode: "march", phase: (t * 2.4) % 1, expr: "grin", blink: blink(1) })
          : bodyFront(p, FRANKLIN_OUTFIT, { mode: "stand", expr: fkExpr, blink: blink(1), wave: shot.id === 8 ? 0.8 : 0.45 }),
      x: SX + 2.2 - fkWalkIn * 1.85,
      y: SY,
      z: SZ + 0.15,
      mirror: shot.id === 1 && fkWalkIn < 0.95,
    });
    if (shot.id === 5 || shot.id === 10) {
      const kidIn = shot.id === 5 ? clamp01((f - shot.a) / 50) : 1;
      places.push({
        key: `fkOther|${shot.id}|${pose}`,
        draw: (p) =>
          shot.id === 5 && kidIn < 0.95
            ? bodySide(p, KID, { mode: "march", phase: (t * 2.8) % 1, expr: "nervous" })
            : bodyFront(p, shot.id === 5 ? KID : townsfolk(1), { mode: "stand", expr: shot.id === 10 ? "dazed" : "nervous" }),
        x: SX + 0.95 + (1 - kidIn) * 1.8,
        y: SY,
        z: SZ + 0.45,
        scale: shot.id === 5 ? 0.84 : 1,
        mirror: shot.id === 5 && kidIn < 0.95,
      });
    }
    if (shot.id === 1 || shot.id >= 14) {
      const fleeU = clamp01((f - shot.a) / 85);
      for (let i = 0; i < 3; i++) {
        places.push({
          key: `fkRun|${shot.id}|${i}|${pose}`,
          draw: (p) =>
            shot.id === 1
              ? bodySide(p, townsfolk(i), { mode: "march", expr: "shock", phase: (t * 3.1 + i * 0.25) % 1 })
              : bodyFront(p, townsfolk(i), { mode: "stand", expr: "grin", wave: 0.6 }),
          x: shot.id === 1 ? SX + 0.2 + i * 0.45 + fleeU * 3.1 : SX + 1.15 + i * 0.55,
          y: SY,
          z: SZ + 0.6 + (i % 2) * 0.2,
        });
      }
    }
    if (shot.id >= 13 && shot.id <= 15 && f % 6 < 3) {
      fxList.push({
        key: `rodGround|${f % 3}`,
        cw: 200,
        ch: 200,
        draw: (p) => fxStars(p, (f % 10) / 10),
        x: SX + 0.65,
        y: SY + 0.35,
        z: SZ - 0.35,
        w: 0.9,
        h: 0.9,
      });
    }

    // Park rug sock shuffle + brass doorknob static zap!
    const shuf = shot.id === 11 || shot.id === 12 ? 0.35 * Math.sin(t * 7) : 0;
    rig.parkZap.visible = shot.id === 12 && f % 3 !== 0;
    if (shot.id === 11 || shot.id === 12) {
      places.push({
        key: `fkRugKid|${pose}`,
        draw: (p) => bodyFront(p, KID, { mode: "march", expr: shot.id === 12 ? "shock" : "grin", phase: (t * 3) % 1, wave: 0.7 }),
        x: PX - 0.35 + shuf,
        y: PY + 0.08,
        z: PZ + 0.1,
        scale: 0.86,
      });
    }
    return;
  }

  if (ep === "tesla") {
    const arcsOn = (shot.id >= 1 && shot.id <= 7) || shot.id === 15;
    rig.teslaArc.visible = arcsOn && f % 2 === 0;
    rig.teslaArc.scale.setScalar(1 + 0.14 * Math.sin(t * 14));
    const bulbsOn = shot.id === 5 || shot.id === 6 || shot.id === 13 || shot.id === 15;
    rig.bulbs.forEach((b, idx) => {
      b.visible = bulbsOn || (shot.id === 1 && idx === 0);
    });
    const boomU = shot.id === 10 ? clamp01((f - shot.a - 15) / 30) : shot.id > 10 ? 0 : 0;
    rig.teslaTower.rotation.z = shot.id === 10 ? boomU * 0.65 : 0;
    rig.moneyBag.visible = shot.id === 3 || shot.id === 4 || shot.id === 8;
    rig.moneyBag.position.x = shot.id === 8 ? 0.35 + clamp01((f - shot.a) / 50) * 1.4 : 0.35;

    if (arcsOn) {
      fxList.push({
        key: `tsArc|${f % 3}`,
        cw: 240,
        ch: 240,
        draw: (p) => fxStars(p, (f % 10) / 10),
        x: SX - 0.95,
        y: SY + 3.05,
        z: SZ - 0.95,
        w: 1.3,
        h: 1.3,
      });
    }
    if (shot.id === 10 && f >= 1310 && f < 1350) {
      fxList.push({
        key: "tsBoom",
        cw: 260,
        ch: 260,
        draw: (p) => fxBurst(p, 0.55),
        x: SX - 0.95,
        y: SY + 1.8,
        z: SZ - 0.7,
        w: 1.8,
        h: 1.6,
      });
    }

    const tsExpr: Expr = shot.id === 8 || shot.id === 10 ? "shock" : shot.id === 15 ? "grin" : "smile";
    places.push({
      key: `ts|${tsExpr}|${pose}|${blink(1) ? 1 : 0}`,
      draw: (p) => bodyFront(p, TESLA_OUTFIT, { mode: "stand", expr: tsExpr, blink: blink(1), wave: 0.5 }),
      x: SX - 0.15,
      y: SY,
      z: SZ + 0.35,
    });
    if (shot.id === 3 || shot.id === 4 || shot.id === 7 || shot.id === 8) {
      const leave = shot.id === 8 ? clamp01((f - shot.a) / 55) * 1.9 : 0;
      const walkOff = shot.id === 8 && leave > 0.05;
      places.push({
        key: `morgan|${shot.id}|${walkOff ? "w" : "s"}|${pose}`,
        draw: (p) =>
          walkOff
            ? bodySide(p, MORGAN_OUTFIT, { mode: "march", expr: "stern", phase: (t * 2.6) % 1 })
            : bodyFront(p, MORGAN_OUTFIT, { mode: "stand", expr: shot.id >= 7 ? "stern" : "grin", phase: (t * 2) % 1 }),
        x: SX + 0.95 + leave,
        y: SY,
        z: SZ + 0.45,
      });
    }
    if (shot.id === 5 || shot.id === 6) {
      const crowdIn = shot.id === 5 ? clamp01((f - shot.a) / 60) : 1;
      for (let i = 0; i < 2; i++) {
        const arrived = crowdIn >= 0.95;
        places.push({
          key: `tsLocal|${i}|${arrived ? "s" : "w"}|${pose}`,
          draw: (p) =>
            arrived
              ? bodyFront(p, townsfolk(i), { mode: "stand", expr: "grin", wave: 0.72 })
              : bodySide(p, townsfolk(i), { mode: "march", expr: "shock", phase: (t * 2.7 + i * 0.3) % 1 }),
          x: SX + 0.75 + i * 0.55 + (1 - crowdIn) * 2.0,
          y: SY,
          z: SZ + 0.55 + i * 0.15,
          mirror: !arrived,
        });
      }
    }
    if (shot.id === 10) {
      const fleeU = clamp01((f - shot.a) / 65);
      for (let i = 0; i < 2; i++) {
        places.push({
          key: `tsCrew|${i}|${pose}`,
          draw: (p) => bodySide(p, townsfolk(i + 2), { mode: "march", expr: "shock", phase: (t * 3.1 + i * 0.25) % 1 }),
          x: SX + 0.45 + i * 0.4 + fleeU * 2.6,
          y: SY,
          z: SZ + 0.55 + i * 0.2,
        });
      }
      if (f % 10 < 5) {
        fxList.push({
          key: `tsDust|${f % 3}`,
          cw: 180,
          ch: 180,
          draw: (p) => fxBurst(p, 0.35),
          x: SX - 0.55,
          y: SY + 0.35,
          z: SZ - 0.4,
          w: 1.4,
          h: 1.0,
        });
      }
    }

    // Park Tuning Forks resonance rings + Wireless phone charger (S11-S12, S14)
    const vib = shot.id === 11 || shot.id === 12 || shot.id === 14 ? 0.03 * Math.sin(t * 26) : 0;
    rig.forkL.position.x = -0.95 + vib;
    rig.forkR.position.x = 0.95 + vib;
    rig.waveRings.forEach((w, i) => {
      const p = ((t * 1.6 + i * 0.33) % 1);
      w.visible = shot.id === 11 || shot.id === 12;
      w.position.set(-0.7 + p * 1.4, 1.15, 0);
      w.scale.setScalar(0.8 + p * 0.9);
    });
    rig.phoneScreen.visible = shot.id === 14;
    if (shot.id === 11 || shot.id === 12 || shot.id === 14) {
      places.push({
        key: `tsPkKid|${pose}`,
        draw: (p) => bodyFront(p, KID, { mode: "stand", expr: "grin", wave: 0.6 }),
        x: PX - 1.5,
        y: PY,
        z: PZ + 0.15,
        scale: 0.84,
      });
      places.push({
        key: `tsPkPar|${pose}`,
        draw: (p) => bodyFront(p, PARENT, { mode: "stand", expr: "smile" }),
        x: PX + 1.5,
        y: PY,
        z: PZ + 0.15,
      });
    }
    return;
  }

  // rontgen
  rig.darkScreenWall.visible = shot.id <= 8;
  const beamOn = (shot.id >= 1 && shot.id <= 3) || (shot.id >= 5 && shot.id <= 8) || shot.id === 13;
  rig.xrayScreen.visible = beamOn;
  rig.xrayBeam.visible = beamOn && f % 2 === 0;
  rig.bonesOverlay.visible = (shot.id >= 5 && shot.id <= 8) || shot.id === 13;
  rig.shoeFootBones.visible = shot.id === 10;

  if (shot.id === 8) {
    fxList.push({
      key: `rgRing|${f % 3}`,
      cw: 220,
      ch: 220,
      draw: (p) => fxStars(p, (f % 10) / 10),
      x: SX + 1.05,
      y: SY + 1.35,
      z: SZ - 0.15,
      w: 0.85,
      h: 0.85,
    });
  }

  const rgExpr: Expr = shot.id === 6 || shot.id === 8 ? "shock" : shot.id >= 9 ? "grin" : "neutral";
  places.push({
    key: `rg|${rgExpr}|${pose}|${blink(1) ? 1 : 0}`,
    draw: (p) => bodyFront(p, RONTGEN_OUTFIT, { mode: "stand", expr: rgExpr, blink: blink(1), wave: shot.id >= 5 && shot.id <= 6 ? 0.85 : 0.35 }),
    x: SX - 0.1,
    y: SY,
    z: SZ + 0.35,
  });

  if (shot.id === 7 || shot.id === 8) {
    const bWalk = shot.id === 7 ? clamp01((f - shot.a) / 50) : 1;
    const arrived = bWalk >= 0.95;
    places.push({
      key: `bertha|${shot.id}|${arrived ? "s" : "w"}|${pose}`,
      draw: (p) =>
        arrived
          ? bodyFront(p, BERTHA_OUTFIT, { mode: "stand", expr: shot.id === 8 ? "shock" : "nervous", wave: 0.65 })
          : bodySide(p, BERTHA_OUTFIT, { mode: "march", expr: "nervous", phase: (t * 2.4) % 1 }),
      x: SX + 0.45 + (1 - bWalk) * 1.9,
      y: SY,
      z: SZ + 0.25,
      mirror: !arrived,
    });
  }
  if (shot.id === 9 || shot.id === 14) {
    const docIn = shot.id === 9 ? clamp01((f - shot.a) / 48) : 1;
    const arrived = docIn >= 0.95;
    places.push({
      key: `rgDoc|${shot.id}|${arrived ? "s" : "w"}|${pose}`,
      draw: (p) =>
        arrived
          ? bodyFront(p, DOC_OUTFIT, { mode: "stand", expr: "grin", wave: 0.55 })
          : bodySide(p, DOC_OUTFIT, { mode: "march", expr: "grin", phase: (t * 2.5) % 1 }),
      x: SX + 1.1 + (1 - docIn) * 1.7,
      y: SY,
      z: SZ + 0.35,
      mirror: !arrived,
    });
    if (shot.id === 14) {
      places.push({
        key: `rgPatient|${pose}`,
        draw: (p) => bodyFront(p, townsfolk(1), { mode: "stand", expr: "smile", wave: 0.4 }),
        x: SX + 1.75,
        y: SY,
        z: SZ + 0.5,
      });
    }
  }
  if (shot.id === 10) {
    const stepU = clamp01((f - shot.a) / 40);
    const onBox = stepU >= 0.92;
    places.push({
      key: `shoeKid|${onBox ? "s" : "w"}|${pose}`,
      draw: (p) =>
        onBox
          ? bodyFront(p, KID, { mode: "stand", expr: "shock" })
          : bodySide(p, KID, { mode: "march", expr: "grin", phase: (t * 2.8) % 1 }),
      x: SX + 0.95 + (1 - stepU) * 1.5,
      y: SY + (onBox ? 0.2 : 0.04 * Math.sin(stepU * Math.PI)),
      z: SZ + 0.4,
      scale: 0.84,
      mirror: !onBox,
    });
  }

  // Park Fence Analogy (S11-S12): Marbles flying straight THROUGH gaps vs bouncing OFF thick steel posts!
  rig.marbles.forEach((m, i) => {
    const u = ((t * 1.3 + i * 0.22) % 1);
    const bounces = i % 2 === 0;
    const zPos = bounces ? (u < 0.5 ? -1.4 + u * 2.6 : -0.1 - (u - 0.5) * 2.4) : -1.4 + u * 2.8;
    const xPos = bounces ? (i === 0 ? -0.95 : i === 2 ? 0 : 0.95) : (i - 2.5) * 0.35;
    m.position.set(xPos, 0.75 + (i % 3) * 0.22, zPos);
    if ((shot.id === 11 || shot.id === 12) && bounces && u > 0.44 && u < 0.58) {
      fxList.push({
        key: `rgHit|${i}|${f % 3}`,
        cw: 150,
        ch: 150,
        draw: (p) => fxBurst(p, 0.3),
        x: PX + xPos,
        y: PY + 0.75 + (i % 3) * 0.22,
        z: PZ - 0.1,
        w: 0.65,
        h: 0.65,
      });
    }
  });
  if (shot.id === 11 || shot.id === 12) {
    places.push({
      key: `rgPkKid|${pose}`,
      draw: (p) => bodyFront(p, KID, { mode: "stand", expr: "grin", wave: 0.7 }),
      x: PX - 1.45,
      y: PY,
      z: PZ - 0.6,
      scale: 0.84,
    });
    places.push({
      key: `rgPkPar|${pose}`,
      draw: (p) => bodyFront(p, PARENT, { mode: "stand", expr: "smile" }),
      x: PX + 1.45,
      y: PY,
      z: PZ - 0.6,
    });
  }
}
