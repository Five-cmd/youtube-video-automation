// Modular historical 3D environments for Batch 1 (pascal, doppler, curie)
// and Batch 2 (foucault, hertz, bernoulli, hooke, homopolar, blackbody).
import * as THREE from "three";
import { twoTone } from "../../bridge/shade";

export function enrichExtraEnvironment(
  ep: string,
  stageGroup: THREE.Group,
  mats: Record<string, THREE.Material>
) {
  const g = new THREE.Group();
  const stoneFloor = twoTone(new THREE.MeshLambertMaterial({ color: "#b8b0a0" }));
  const darkFloor = twoTone(new THREE.MeshLambertMaterial({ color: "#3b3026" }));
  const brick = twoTone(new THREE.MeshLambertMaterial({ color: "#884638" }));
  const plaster = twoTone(new THREE.MeshLambertMaterial({ color: "#d4ccb8" }));
  const slate = twoTone(new THREE.MeshLambertMaterial({ color: "#353c48" }));
  const concrete = twoTone(new THREE.MeshLambertMaterial({ color: "#7f858d" }));

  if (ep === "pascal") {
    // 1646 Rouen half-timbered stone house facade & wooden pouring balcony
    const wall = new THREE.Mesh(new THREE.BoxGeometry(10, 5.4, 1.4), plaster);
    wall.position.set(-1.5, 2.7, -5.6);
    const roof = new THREE.Mesh(new THREE.BoxGeometry(10.6, 0.35, 2.2), slate);
    roof.position.set(-1.5, 5.55, -5.4);
    const balc = new THREE.Mesh(new THREE.BoxGeometry(2.6, 0.16, 1.2), mats.wood);
    balc.position.set(-0.65, 4.35, -1.8);
    g.add(wall, roof, balc);
    for (const tx of [-5.2, -3.2, -1.2, 0.8, 2.6]) {
      const beam = new THREE.Mesh(new THREE.BoxGeometry(0.16, 5.4, 0.16), mats.wood);
      beam.position.set(tx, 2.7, -4.85);
      g.add(beam);
    }
  } else if (ep === "doppler") {
    // 1845 Utrecht wooden railway sleepers + Victorian station canopy pillars
    for (let sx = -10; sx <= 10; sx += 1.0) {
      const tie = new THREE.Mesh(new THREE.BoxGeometry(0.24, 0.08, 1.75), mats.wood);
      tie.position.set(sx, 0.06, -0.5);
      g.add(tie);
    }
    const canopy = new THREE.Mesh(new THREE.BoxGeometry(10.5, 0.18, 2.6), slate);
    canopy.position.set(0.5, 2.85, 1.4);
    g.add(canopy);
    for (const px of [-3.5, 0.5, 4.5]) {
      const col = new THREE.Mesh(new THREE.CylinderGeometry(0.08, 0.1, 2.8, 8), mats.iron);
      col.position.set(px, 1.4, 2.2);
      g.add(col);
    }
  } else if (ep === "curie") {
    // 1898 Paris shed timber floor, rafters & glowing pitchblende ore chunks
    const floor = new THREE.Mesh(new THREE.BoxGeometry(12, 0.1, 10), darkFloor);
    floor.position.set(0, -0.05, -0.5);
    g.add(floor);
    for (const rx of [-2.8, 0, 2.8]) {
      const rafter = new THREE.Mesh(new THREE.BoxGeometry(0.18, 0.22, 4.2), mats.wood);
      rafter.position.set(rx, 4.1, -0.2);
      g.add(rafter);
    }
  } else if (ep === "foucault") {
    // 1851 Paris Pantheon checkered marble floor & neoclassical columns
    const floor = new THREE.Mesh(new THREE.BoxGeometry(16, 0.12, 16), stoneFloor);
    floor.position.set(0, -0.06, -1.0);
    g.add(floor);
    for (const cx of [-4.2, -2.1, 2.1, 4.2]) {
      const col = new THREE.Mesh(new THREE.CylinderGeometry(0.26, 0.3, 4.8, 12), plaster);
      col.position.set(cx, 2.4, -4.6);
      g.add(col);
    }
  } else if (ep === "hertz") {
    // 1887 Karlsruhe Physics Lecture Lab floor & workbench
    const floor = new THREE.Mesh(new THREE.BoxGeometry(12, 0.12, 10), darkFloor);
    floor.position.set(0, -0.06, -0.5);
    const bench = new THREE.Mesh(new THREE.BoxGeometry(3.8, 0.9, 1.1), mats.wood);
    bench.position.set(0, 0.45, -0.2);
    g.add(floor, bench);
  } else if (ep === "bernoulli") {
    // Airfield runway apron & wind-tunnel hangar arch
    const runway = new THREE.Mesh(new THREE.BoxGeometry(18, 0.12, 16), concrete);
    runway.position.set(0, -0.06, -1.0);
    const hangar = new THREE.Mesh(new THREE.BoxGeometry(9.0, 4.0, 2.4), slate);
    hangar.position.set(0, 2.0, -5.8);
    g.add(runway, hangar);
  } else if (ep === "hooke") {
    // 1665 Royal Society oak study floor, desk & tall library shelves
    const floor = new THREE.Mesh(new THREE.BoxGeometry(12, 0.12, 10), darkFloor);
    floor.position.set(0, -0.06, -0.5);
    const desk = new THREE.Mesh(new THREE.BoxGeometry(3.2, 0.78, 1.2), mats.wood);
    desk.position.set(0, 0.39, -0.25);
    const shelf = new THREE.Mesh(new THREE.BoxGeometry(5.6, 3.8, 0.6), mats.wood);
    shelf.position.set(0, 1.9, -3.2);
    g.add(floor, desk, shelf);
  } else if (ep === "homopolar") {
    // 1821 Royal Institution lab floor, table & brass voltaic pile
    const floor = new THREE.Mesh(new THREE.BoxGeometry(12, 0.12, 10), darkFloor);
    floor.position.set(0, -0.06, -0.5);
    const table = new THREE.Mesh(new THREE.BoxGeometry(3.2, 0.78, 1.2), mats.wood);
    table.position.set(0, 0.39, -0.2);
    const pile = new THREE.Mesh(new THREE.CylinderGeometry(0.18, 0.18, 0.68, 12), mats.copper);
    pile.position.set(1.05, 1.12, -0.2);
    g.add(floor, table, pile);
  } else if (ep === "blackbody") {
    // 1900 Berlin brick furnace hearth & iron chimney
    const floor = new THREE.Mesh(new THREE.BoxGeometry(12, 0.12, 10), darkFloor);
    floor.position.set(0, -0.06, -0.5);
    const hearth = new THREE.Mesh(new THREE.BoxGeometry(2.6, 1.8, 1.4), brick);
    hearth.position.set(-1.8, 0.9, -1.2);
    const flue = new THREE.Mesh(new THREE.CylinderGeometry(0.28, 0.32, 3.2, 10), mats.iron);
    flue.position.set(-1.8, 3.2, -1.2);
    g.add(floor, hearth, flue);
  }

  stageGroup.add(g);
}
