#!/usr/bin/env bash
# Downloads Kenney CC0 kits (Nature Kit + Fantasy Town Kit) and copies the GLBs the world loads into $1.
# Kenney's zip links carry a hash, so the link is scraped from the asset page. Missing models are skipped by world.ts.
set -u
DEST="${1:-public/bridge/kenney}"
mkdir -p "$DEST" /tmp/kenney
for kit in nature-kit fantasy-town-kit; do
  url=$(curl -sL "https://kenney.nl/assets/$kit" | grep -oE 'https://kenney\.nl/media/pages/assets/[^"]+\.zip' | head -n1)
  if [ -z "$url" ]; then echo "no zip link for $kit"; continue; fi
  curl -sL "$url" -o "/tmp/kenney/$kit.zip" && unzip -oq "/tmp/kenney/$kit.zip" -d "/tmp/kenney/$kit" || echo "download failed: $kit"
done
find /tmp/kenney -iname '*.glb' -exec cp -n {} "$DEST/" \;
echo "kenney models: $(ls "$DEST" | wc -l)"
