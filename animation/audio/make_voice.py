"""Voice + word timings for a cartoon short (pipeline step 3). Light network job, no rendering.
usage: python make_voice.py <short_dir> [voice] [rate]
Reads <short_dir>/SCRIPT.md (lines under '## Script'), writes voice/voice.mp3, voice/voice.wav (48 kHz) and voice/words.json.
"""
import asyncio
import json
import subprocess
import sys
from pathlib import Path

import edge_tts
import imageio_ffmpeg


def script_text(md: Path) -> str:
    lines, on = [], False
    for ln in md.read_text(encoding="utf-8").splitlines():
        if ln.startswith("## "):
            on = ln.lower().startswith("## script")
            continue
        if on and ln.strip() and not ln.startswith("#"):
            lines.append(ln.strip())
    if not lines:
        # fallback for SCRIPT_example.md where script lines follow 'Facts:'
        for ln in md.read_text(encoding="utf-8").splitlines():
            if ln.strip() and not ln.startswith(("#", "Format:", "Facts:", "nobody killed")):
                lines.append(ln.strip())
    return " ".join(lines)


async def main(d: Path, voice: str, rate: str):
    out = d / "voice"
    out.mkdir(parents=True, exist_ok=True)
    text = script_text(d / "SCRIPT.md")
    com = edge_tts.Communicate(text, voice, rate=rate, boundary="WordBoundary")
    words, audio = [], bytearray()
    async for ch in com.stream():
        if ch["type"] == "audio":
            audio += ch["data"]
        elif ch["type"] == "WordBoundary":
            s = round(ch["offset"] / 1e7, 3)
            e = round((ch["offset"] + ch["duration"]) / 1e7, 3)
            words.append({"w": ch["text"], "s": s, "e": e, "word": ch["text"], "start": s, "end": e})
    (out / "voice.mp3").write_bytes(audio)
    subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-loglevel", "error", "-i", str(out / "voice.mp3"),
                    "-ar", "48000", "-ac", "1", str(out / "voice.wav")], check=True)
    (out / "words.json").write_text(json.dumps(words, indent=1), encoding="utf-8")
    dur = words[-1]["e"] if words else 0
    print(f"[{d.name}] {len(words)} words, {dur:.2f} s, {len(words) / max(dur, 1e-6):.2f} words/s")


if __name__ == "__main__":
    d = Path(sys.argv[1])
    default_rate = "+8%" if d.name == "bridge" else "+25%"
    asyncio.run(main(d, sys.argv[2] if len(sys.argv) > 2 else "en-US-GuyNeural", sys.argv[3] if len(sys.argv) > 3 else default_rate))
