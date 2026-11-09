// Cloud (Linux, no GPU) still renderer for look checks.
// usage: node scripts/cloud-stills.mjs <compId> <outPrefix> <frame,frame,...> [scale]
// Reuses a single headless browser instance via openBrowser() so texture caches persist across stills.
import fs from "node:fs";
import path from "node:path";
import { bundle } from "@remotion/bundler";
import { openBrowser, renderStill, selectComposition } from "@remotion/renderer";

const [comp = "BridgeShort", prefix = "out/stills/x_", frames = "100,400", scale = "0.5"] = process.argv.slice(2);
fs.mkdirSync(path.dirname(prefix), { recursive: true });
const chromiumOptions = { gl: "swangle" };
const serveUrl = await bundle({ entryPoint: path.resolve("src/index.ts"), publicDir: path.resolve("public") });
const puppeteerInstance = await openBrowser("chrome", { chromiumOptions });
try {
  const composition = await selectComposition({ serveUrl, id: comp, puppeteerInstance, chromiumOptions });
  const onBrowserLog = (l) => { if (l.type === "error" || l.type === "warning") console.log(`[${l.type}]`, l.text.slice(0, 300)); };
  for (const f of frames.split(",").map(Number)) {
    const t0 = Date.now();
    await renderStill({
      composition, serveUrl, frame: f, output: `${prefix}${f}.jpg`, imageFormat: "jpeg", jpegQuality: 88,
      scale: Number(scale), puppeteerInstance, chromiumOptions, timeoutInMilliseconds: 600000, onBrowserLog,
    });
    console.log("still", comp, f, ((Date.now() - t0) / 1000).toFixed(1) + "s");
  }
} finally {
  await puppeteerInstance.close({ silent: true });
}
