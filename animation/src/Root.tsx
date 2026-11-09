import React from "react";
import { Composition } from "remotion";
import { BridgeShort, BRIDGE_FRAMES } from "./videos/bridge/Bridge";
import { CavendishShort, MagdeburgShort, FaradayShort, EP_FRAMES } from "./videos/physics/PhysicsShort";

// 4 Major Physics Shorts (4x/day cartoon-3d-short pipeline):
//  1. BridgeShort    - Mechanical Resonance (Broughton Suspension Bridge, 1831)
//  2. CavendishShort - Universal Gravitation (Henry Cavendish Torsion Balance, 1797)
//  3. MagdeburgShort - Atmospheric Pressure (Magdeburg Hemispheres, 1654)
//  4. FaradayShort   - Electromagnetism (Michael Faraday Cage, 1836)
export const Root: React.FC = () => (
  <>
    <Composition id="BridgeShort" component={BridgeShort} durationInFrames={BRIDGE_FRAMES} fps={30} width={1080} height={1920} />
    <Composition id="CavendishShort" component={CavendishShort} durationInFrames={EP_FRAMES.cavendish} fps={30} width={1080} height={1920} />
    <Composition id="MagdeburgShort" component={MagdeburgShort} durationInFrames={EP_FRAMES.magdeburg} fps={30} width={1080} height={1920} />
    <Composition id="FaradayShort" component={FaradayShort} durationInFrames={EP_FRAMES.faraday} fps={30} width={1080} height={1920} />
  </>
);
