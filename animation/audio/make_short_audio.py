"""Cloud audio generator & -15.0 LUFS master for any of the 4 physics shorts.
usage: python animation/audio/make_short_audio.py <CompId>
Writes animation/out/<CompId>/mix.wav (48 kHz, stereo, 24-bit, -15.0 LUFS integrated, <= -1.2 dBTP true peak).
"""
import json
import os
import subprocess
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ANIM = HERE.parent
sys.path.insert(0, str(HERE))

from dsp import SR, ns, st, dbg, read_wav, write_wav, integrated, true_peak  # noqa: E402
import mix as M  # noqa: E402

COMP_MAP = {
    "BridgeShort": ("bridge", 2025 / 30.0),
    "CavendishShort": ("cavendish", 2070 / 30.0),
    "MagdeburgShort": ("magdeburg", 1965 / 30.0),
    "FaradayShort": ("faraday", 2010 / 30.0),
}


def fit_len(x: np.ndarray, target_n: int) -> np.ndarray:
    """Pad or trim a stereo array (2, N) to (2, target_n) with a clean 30 ms fade-out."""
    cur = x.shape[1]
    if cur >= target_n:
        out = x[:, :target_n].copy()
    else:
        out = np.zeros((2, target_n), dtype=np.float64)
        out[:, :cur] = x
        # softly loop tail bed if target_n > cur
        rem = target_n - cur
        out[:, cur:] = x[:, -rem:] * 0.5
    fade = min(ns(0.04), target_n)
    out[:, -fade:] *= np.linspace(1.0, 0.0, fade)[None, :]
    return out


def build_audio(comp: str) -> Path:
    slug, dur = COMP_MAP.get(comp, ("bridge", 67.5))
    short_dir = ANIM / "shorts" / slug
    voice_wav = short_dir / "voice" / "voice.wav"
    words_json = short_dir / "voice" / "words.json"
    if not voice_wav.exists() or not words_json.exists():
        subprocess.run([sys.executable, str(HERE / "make_voice.py"), str(short_dir), "en-US-GuyNeural", "+25%"], check=True)

    # Also keep animation/voice/ populated for mix.py cache compatibility
    vdir = ANIM / "voice"
    vdir.mkdir(parents=True, exist_ok=True)
    if not (vdir / "voice.wav").exists():
        (vdir / "voice.wav").write_bytes(voice_wav.read_bytes())
        (vdir / "words.json").write_bytes(words_json.read_bytes())

    target_n = ns(dur)
    x, sr = read_wav(str(voice_wav))
    assert sr == SR, f"Expected {SR} Hz, got {sr}"
    v_mono = x[0] if x.shape[0] == 1 else x.mean(0)
    v = np.zeros(target_n, dtype=np.float64)
    v[: min(target_n, len(v_mono))] = v_mono[:target_n]
    v = st(v)
    v_ref = integrated(v)

    words = json.loads(words_json.read_text(encoding="utf-8"))
    spans = M.speech_spans(words)

    # Synthesize original march/chamber score + SFX via music.py and sfx.py (cached in _cache/)
    import music
    import sfx

    m_raw = M.cached("music_raw", lambda: music.render(music.build(), ref=-20.0)[0])
    s_raw = M.cached("sfx", lambda: sfx.render(v_ref)[0])

    m_fit = fit_len(m_raw, target_n)
    s_fit = fit_len(s_raw, target_n)

    # Keyed -3 dB speech ducking on the music bed from words.json
    ctrl = 1000
    nc = int(dur * ctrl) + 2
    va = np.zeros(nc)
    for s_t, e_t in spans:
        va[max(0, int((s_t - 0.08) * ctrl)): int((e_t + 0.12) * ctrl)] = 1.0
    ka, kr = 1 - np.exp(-1 / (0.07 * ctrl)), 1 - np.exp(-1 / (0.45 * ctrl))
    env = np.zeros(nc)
    e_v = 0.0
    for i in range(nc):
        tgt = va[i]
        e_v += (tgt - e_v) * (ka if tgt > e_v else kr)
        env[i] = e_v
    dk = np.interp(np.arange(target_n) / SR, np.arange(nc) / ctrl, M.DUCK_DB * env)
    m_ducked = m_fit * dbg(dk)[None, :]

    # Align music integrated loudness to -10.5 LU below speech
    Lm = integrated(m_ducked)
    if np.isfinite(Lm):
        m_ducked *= dbg((v_ref - 10.5) - Lm)

    pre = v + m_ducked + s_fit
    g_master = dbg(M.TARGET_LUFS - integrated(pre))
    master, _ = M.limiter(pre * g_master)
    # Fine trim to hit -15.0 LUFS after limiting
    master *= dbg(M.TARGET_LUFS - integrated(master))
    master, _ = M.limiter(master)

    out_dir = ANIM / "out" / comp
    out_dir.mkdir(parents=True, exist_ok=True)
    out_wav = out_dir / "mix.wav"
    write_wav(str(out_wav), master)
    print(f"[{comp}] Master mix -> {out_wav} | {integrated(master):.2f} LUFS | TP {true_peak(master):.2f} dBTP | {dur:.2f} s")
    return out_wav


if __name__ == "__main__":
    comp_id = sys.argv[1] if len(sys.argv) > 1 else "BridgeShort"
    build_audio(comp_id)
