"""Voice + word timings for a cartoon short (pipeline step 3).
Generates expressive speech with rich intonation, natural storytelling cadence,
and per-episode vocal personality.
usage: python make_voice.py <short_dir> [voice] [rate] [pitch]
"""
import asyncio
import json
import re
import subprocess
import sys
from pathlib import Path

import edge_tts
import imageio_ffmpeg

# Storyteller voices with high expression & distinct personality per topic:
# - faraday (Victorian science drama): en-US-ChristopherNeural (warm, articulate, theatrical)
# - bridge (Military history / suspense): en-US-AndrewMultilingualNeural (grounded, dramatic, engaging)
# - default: en-US-BrianMultilingualNeural (clear, expressive story narrator)
VOICE_MAP = {
    "faraday": "en-US-ChristopherNeural",
    "bridge": "en-US-AndrewMultilingualNeural",
    "cavendish": "en-US-ChristopherNeural",
    "magdeburg": "en-US-BrianMultilingualNeural",
}


def script_text(md: Path) -> str:
    lines, on = [], False
    for ln in md.read_text(encoding="utf-8").splitlines():
        if ln.startswith("## "):
            on = ln.lower().startswith("## script")
            continue
        if on and ln.strip() and not ln.startswith("#"):
            lines.append(ln.strip())
    if not lines:
        for ln in md.read_text(encoding="utf-8").splitlines():
            if ln.strip() and not ln.startswith(("#", "Format:", "Facts:", "nobody killed")):
                lines.append(ln.strip())
    
    # Clean text to give natural pauses:
    # Ensure em-dashes and ellipses have breathing room for natural voice inflections
    full = " ".join(lines)
    full = full.replace("—", ", ")
    full = full.replace("...", "... ")
    return full


async def main(d: Path, voice: str | None = None, rate: str | None = None, pitch: str | None = None):
    out = d / "voice"
    out.mkdir(parents=True, exist_ok=True)
    slug = d.name.lower()
    
    # 1. Pick natural storytelling voice & cadence
    sel_voice = voice or VOICE_MAP.get(slug, "en-US-ChristopherNeural")
    
    # More relaxed, natural speech rate (was +25% which sounded rushed and robotic)
    # +10% to +12% gives perfect punchy YouTube Shorts energy without losing human cadence
    sel_rate = rate or ("+10%" if slug in ("bridge", "faraday") else "+12%")
    sel_pitch = pitch or "+0Hz"

    text = script_text(d / "SCRIPT.md")
    print(f"[{slug}] Synthesizing with voice='{sel_voice}', rate='{sel_rate}', pitch='{sel_pitch}'...")

    com = edge_tts.Communicate(text, sel_voice, rate=sel_rate, pitch=sel_pitch, boundary="WordBoundary")
    words, audio = [], bytearray()
    async for ch in com.stream():
        if ch["type"] == "audio":
            audio += ch["data"]
        elif ch["type"] == "WordBoundary":
            s = round(ch["offset"] / 1e7, 3)
            e = round((ch["offset"] + ch["duration"]) / 1e7, 3)
            words.append({"w": ch["text"], "s": s, "e": e, "word": ch["text"], "start": s, "end": e})
            
    mp3_path = out / "voice.mp3"
    wav_path = out / "voice.wav"
    mp3_path.write_bytes(audio)
    
    # Convert to 48kHz mono WAV with broadcast quality high-shelf & speech clarity EQ
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    # Apply warm vocal presence filter: highpass 80Hz + gentle warm presence boost at 3kHz
    vf = "highpass=f=80,equalizer=f=3000:t=q:w=1.2:g=2.0"
    subprocess.run([
        ffmpeg_exe, "-y", "-loglevel", "error", "-i", str(mp3_path),
        "-af", vf,
        "-ar", "48000", "-ac", "1", str(wav_path)
    ], check=True)
    
    (out / "words.json").write_text(json.dumps(words, indent=1), encoding="utf-8")
    dur = words[-1]["e"] if words else 0
    print(f"[{slug}] Done: {len(words)} words, {dur:.2f} s ({len(words) / max(dur, 1e-6):.2f} words/s)")


if __name__ == "__main__":
    d = Path(sys.argv[1])
    v = sys.argv[2] if len(sys.argv) > 2 else None
    r = sys.argv[3] if len(sys.argv) > 3 else None
    p = sys.argv[4] if len(sys.argv) > 4 else None
    asyncio.run(main(d, v, r, p))
