import React from "react";
import { Composition } from "remotion";
import { BridgeShort, BRIDGE_FRAMES } from "./videos/bridge/Bridge";
import {
  CavendishShort, MagdeburgShort, FaradayShort,
  GalileoShort, ArchimedesShort, NewtonShort, FranklinShort, TeslaShort, RontgenShort,
  EP_FRAMES,
} from "./videos/physics/PhysicsShort";

export const Root: React.FC = () => (
  <>
    <Composition id="BridgeShort" component={BridgeShort} durationInFrames={BRIDGE_FRAMES} fps={30} width={1080} height={1920} />
    <Composition id="CavendishShort" component={CavendishShort} durationInFrames={EP_FRAMES.cavendish} fps={30} width={1080} height={1920} />
    <Composition id="MagdeburgShort" component={MagdeburgShort} durationInFrames={EP_FRAMES.magdeburg} fps={30} width={1080} height={1920} />
    <Composition id="FaradayShort" component={FaradayShort} durationInFrames={EP_FRAMES.faraday} fps={30} width={1080} height={1920} />
    <Composition id="GalileoShort" component={GalileoShort} durationInFrames={EP_FRAMES.galileo} fps={30} width={1080} height={1920} />
    <Composition id="ArchimedesShort" component={ArchimedesShort} durationInFrames={EP_FRAMES.archimedes} fps={30} width={1080} height={1920} />
    <Composition id="NewtonShort" component={NewtonShort} durationInFrames={EP_FRAMES.newton} fps={30} width={1080} height={1920} />
    <Composition id="FranklinShort" component={FranklinShort} durationInFrames={EP_FRAMES.franklin} fps={30} width={1080} height={1920} />
    <Composition id="TeslaShort" component={TeslaShort} durationInFrames={EP_FRAMES.tesla} fps={30} width={1080} height={1920} />
    <Composition id="RontgenShort" component={RontgenShort} durationInFrames={EP_FRAMES.rontgen} fps={30} width={1080} height={1920} />
  </>
);
