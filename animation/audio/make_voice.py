"""Voice + word timings for a cartoon short (pipeline step 3).
Matched to punchy YouTube Shorts documentary narrator style (crisp cadence, warm low-mid,
dynamic intonation, clear phrasing).
usage: python make_voice.py <short_dir> [voice] [rate] [pitch]
"""
import asyncio
import json
import subprocess
import sys
from pathlib import Path

import edge_tts
import imageio_ffmpeg

# Primary narrator: AndrewMultilingualNeural (+15% rate, -2Hz pitch) matches modern punchy
# YouTube Shorts explainer style (crisp, confident, warm chest tone, natural emphasis).
VOICE_MAP = {
    "faraday": "en-US-ChristopherNeural",
    "bridge": "en-US-AndrewMultilingualNeural",
    "cavendish": "en-US-ChristopherNeural",
    "magdeburg": "en-US-BrianMultilingualNeural",
    "galileo": "en-US-AndrewMultilingualNeural",
    "archimedes": "en-US-AndrewMultilingualNeural",
    "newton": "en-US-AndrewMultilingualNeural",
    "franklin": "en-US-AndrewMultilingualNeural",
    "tesla": "en-US-AndrewMultilingualNeural",
    "rontgen": "en-US-AndrewMultilingualNeural",
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

    # Preserve crisp micro-pauses on em-dashes and ellipses for punchy documentary cadence
    full = " ".join(lines)
    full = full.replace("—", ", ")
    full = full.replace("...", "... ")
    return full


async def main(d: Path, voice: str | None = None, rate: str | None = None, pitch: str | None = None):
    out = d / "voice"
    out.mkdir(parents=True, exist_ok=True)
    slug = d.name.lower()

    sel_voice = voice or VOICE_MAP.get(slug, "en-US-AndrewMultilingualNeural")
    sel_rate = rate or "+15%"
    sel_pitch = pitch or "+0Hz"

    text = script_text(d / "SCRIPT.md")
    attempts = [
        (sel_voice, sel_rate, sel_pitch),
        (sel_voice, sel_rate, "+0Hz"),
        ("en-US-ChristopherNeural", "+12%", "+0Hz"),
    ]
    words, audio = [], bytearray()
    for v_try, r_try, p_try in attempts:
        try:
            print(f"[{slug}] Synthesizing with voice='{v_try}', rate='{r_try}', pitch='{p_try}'...")
            com = edge_tts.Communicate(text, v_try, rate=r_try, pitch=p_try, boundary="WordBoundary")
            words, audio = [], bytearray()
            async for ch in com.stream():
                if ch["type"] == "audio":
                    audio += ch["data"]
                elif ch["type"] == "WordBoundary":
                    s = round(ch["offset"] / 1e7, 3)
                    e = round((ch["offset"] + ch["duration"]) / 1e7, 3)
                    words.append({"w": ch["text"], "s": s, "e": e, "word": ch["text"], "start": s, "end": e})
            if audio:
                break
        except Exception as err:
            print(f"[{slug}] TTS attempt ({v_try}, {p_try}) failed: {err}")
    if not audio:
        raise RuntimeError(f"[{slug}] All TTS attempts failed")

    mp3_path = out / "voice.mp3"
    wav_path = out / "voice.wav"
    mp3_path.write_bytes(audio)

    # Broadcast documentary chain: rumble cut (80Hz) + warm chest (+1.5dB @ 180Hz) +
    # crisp vocal clarity (+2.5dB @ 3.5kHz) + gentle leveling compressor
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    vf = (
        "highpass=f=80,"
        "equalizer=f=180:t=q:w=1.0:g=1.5,"
        "equalizer=f=3500:t=q:w=1.2:g=2.5,"
        "acompressor=threshold=-18dB:ratio=2.5:attack=10:release=120:makeup=2"
    )
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
