import React from "react";
import { Composition } from "remotion";
import { BridgeShort, BRIDGE_FRAMES } from "./videos/bridge/Bridge";

// One composition per short. New physics shorts: copy videos/bridge -> videos/<name>, edit story.ts / build.ts / cast.ts,
// and register it here next to BridgeShort (pipeline step 4 of the cartoon-3d-short skill).
export const Root: React.FC = () => (
  <>
    <Composition id="BridgeShort" component={BridgeShort} durationInFrames={BRIDGE_FRAMES} fps={30} width={1080} height={1920} />
  </>
);
