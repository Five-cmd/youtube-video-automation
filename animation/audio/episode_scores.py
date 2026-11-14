"""Original episode-specific score & SFX generators for CavendishShort, MagdeburgShort, and FaradayShort.
Each episode gets its own distinct musical key, tempo, instrumentation, melody, and physical SFX cues:
- CavendishShort (1797): D minor -> D major 18th-century chamber mystery (plucked harpsichord/pizzicato strings,
  ticking vibraphone/glockenspiel pendulum, warm strings pad, low timpani pulse, telescope/draft/bell SFX).
- MagdeburgShort (1654): G major -> E minor -> G major Imperial Baroque Brass & Timpani Fanfare (royal trumpets/horns,
  tuba bass, marching snare/timpani tug-of-war drive, pump hiss, whip cracks, horse hooves, vacuum pop SFX).
- FaradayShort (1836): A minor -> F major -> C major Victorian Electric Scherzo (staccato string/musicbox arpeggios,
  vibraphone/glockenspiel sparks, tense brass/timpani build, glass wheel hum, electric crackle & thunderbolt SFX).
"""
import math
import numpy as np
from dsp import (SR, TAU, ns, tt, rng, dbg, lp, hp, bp, peq, shelf, pan, st, place, fades, widen,
                 make_ir, convolve_st, momentary_max, integrated, colored, smooth_noise, modal, phase)
import instruments as I
import sfx_gen as G

F = I.m2f


class EpBand:
    def __init__(self, n_samples: int):
        self.N = n_samples
        self.tr = {}
        self.send = {}

    def track(self, name: str, send: float = 0.18):
        if name not in self.tr:
            self.tr[name] = np.zeros((2, self.N))
            self.send[name] = send
        return self.tr[name]

    def add(self, name: str, x, t: float, p: float = 0.0, g: float = 1.0, send: float = 0.18):
        buf = self.track(name, send)
        place(buf, pan(x, p) if np.ndim(x) == 1 else x, t, g)


def render_band(b: EpBand, ref: float = -20.0, targets: dict | None = None):
    tgt_map = targets or {
        "lead": -1.5, "counter": -3.5, "pluck": -3.0, "bass": -2.5, "pad": -3.5,
        "brass": -2.5, "perc": -5.5, "bell": -4.5, "spark": -4.0,
    }
    hall = make_ir(1.6, 19, pre=0.018, hf=1.4)
    dry = np.zeros((2, b.N))
    wet = np.zeros((2, b.N))
    for k, x in b.tr.items():
        if not np.any(x):
            continue
        L = integrated(x)
        if np.isfinite(L):
            x = x * dbg(ref + tgt_map.get(k, -5.0) - L)
        b.tr[k] = x
        dry += x
        wet += b.send.get(k, 0.18) * x
    out = dry + 0.72 * convolve_st(wet.mean(0), hall)
    return hp(out, 30, 2)


# ==============================================================================
# 1. CAVENDISH SHORT (1797) - "Chamber Mystery & Pendulum" (D minor / D major, 108 BPM)
# ==============================================================================
def build_cavendish_music(dur: float) -> np.ndarray:
    N = ns(dur)
    b = EpBand(N)
    R = rng(1797)
    _r = lambda: rng(int(R.integers(1 << 30)))
    Q = 60.0 / 108.0  # 0.555s per beat
    FLASH = 130.0 / 30.0

    # Hook (0 -> 4.33s): Plucked harpsichord/pizzicato D minor arpeggio + mysterious glockenspiel
    hook_notes = [62, 65, 69, 74, 73, 69, 65, 62]
    for i, m in enumerate(hook_notes):
        t = i * (FLASH / 8.0)
        b.add("pluck", I.pluck(F(m), 0.82, _r(), dur=0.65, bright=0.75), t, -0.2 + 0.05 * i)
        if i % 2 == 0:
            b.add("bell", I.musicbox(F(m + 12), 0.55, _r()), t, 0.25)
    b.add("bass", I.pluck(F(38), 0.95, _r(), dur=1.2), 0.0, -0.1)
    b.add("bass", I.pluck(F(45), 0.9, _r(), dur=1.2), FLASH * 0.5, -0.1)
    # Flash button chord
    for m in [50, 57, 62, 65, 69]:
        b.add("lead", I.pluck(F(m), 0.85, _r(), dur=0.9, bright=0.8), FLASH, 0.0)
    b.add("bell", I.glock(F(86), 0.7, _r()), FLASH, 0.2)

    # Story & Apparatus (4.8s -> 28.0s): Ticking torsion-balance chamber waltz/ostinato in D minor
    prog_dm = [
        ([50, 53, 57], 38, [74, 77, 81, 77]),  # Dm
        ([46, 50, 53], 46, [70, 74, 77, 74]),  # Bb
        ([43, 46, 50], 43, [67, 70, 74, 79]),  # Gm
        ([45, 49, 52], 45, [69, 73, 76, 73]),  # A7
    ]
    t_cur = 4.8
    bar = 0
    while t_cur < 28.0:
        ch_triad, bass_m, arp = prog_dm[bar % 4]
        # Bass pizzicato on beat 1 and 3
        b.add("bass", I.pluck(F(bass_m), 0.8, _r(), dur=0.9), t_cur, -0.1)
        b.add("bass", I.pluck(F(bass_m + 7), 0.65, _r(), dur=0.7), t_cur + 2 * Q, -0.1)
        # Warm chamber pad underneath
        b.add("pad", I.pad([F(m) for m in ch_triad], 4 * Q, 0.35, _r(), att=0.3, rel=0.4, warm=800), t_cur, 0.0)
        # Delicate harpsichord/pizzicato eighth-note filigree
        for k, m in enumerate(arp):
            b.add("pluck", I.pluck(F(m), 0.6, _r(), dur=0.45, bright=0.65), t_cur + k * Q, -0.25 + 0.15 * (k % 2))
            if bar >= 2 and k in (0, 2):
                b.add("lead", I.vibes(F(m), 0.52, _r(), dur=1.1, damp=0.8), t_cur + k * Q, 0.22)
        t_cur += 4 * Q
        bar += 1

    # Tension & Creeping Millimetres (28.0s -> 37.8s): High-precision clockwork ticking + rising chromatic bass
    t_tick = 28.0
    step = 0
    while t_tick < 33.0:
        m_top = 86 + (step % 4)
        b.add("bell", I.musicbox(F(m_top), 0.5 + 0.02 * step, _r(), dur=0.4), t_tick, 0.3 * (1 if step % 2 else -1))
        if step % 2 == 0:
            b.add("bass", I.pluck(F(38 + (step // 2) % 6), 0.78, _r(), dur=0.6), t_tick, -0.1)
        t_tick += Q * 0.5
        step += 1
    # Shot 8 Climax (33.0s): The microscopic deflection lands -> crystalline vibraphone + warm low timpani resonance
    b.add("perc", I.timpani(F(38), 0.75, _r(), dur=2.4), 33.3, -0.1)
    for k, m in enumerate([62, 66, 69, 74, 78, 86]):
        b.add("lead", I.vibes(F(m), 0.7, _r(), dur=2.2), 33.3 + k * 0.09, -0.3 + 0.12 * k)
        b.add("bell", I.glock(F(m + 12), 0.55, _r(), dur=1.8), 33.35 + k * 0.09, 0.3 - 0.1 * k)

    # Golden Hour Park Analogy (43.5s -> 58.0s): Warm D major pastoral chamber music (vibes + musicbox + pizzicato)
    prog_DM = [
        ([50, 54, 57], 38, [74, 78, 81, 86]),  # D major
        ([47, 50, 54], 47, [71, 74, 78, 81]),  # Bm
        ([43, 47, 50], 43, [67, 71, 74, 79]),  # G major
        ([45, 49, 52], 45, [69, 73, 76, 81]),  # A major
    ]
    t_cur = 43.5
    bar = 0
    while t_cur < 58.2:
        ch_triad, bass_m, mel = prog_DM[bar % 4]
        b.add("pad", I.pad([F(m) for m in ch_triad], 4 * Q, 0.45, _r(), att=0.4, rel=0.5, warm=950), t_cur, 0.0)
        b.add("bass", I.pluck(F(bass_m), 0.75, _r(), dur=1.0), t_cur, -0.1)
        for k, m in enumerate(mel):
            b.add("lead", I.vibes(F(m), 0.58, _r(), dur=1.2, damp=0.7), t_cur + k * Q, -0.2)
            b.add("bell", I.musicbox(F(m + 12), 0.48, _r()), t_cur + k * Q + Q * 0.5, 0.25)
        t_cur += 4 * Q
        bar += 1

    # Grand Weigh-the-Earth Reveal & Tiptoe Callback (58.2s -> dur):
    # Majestic D major chord on "six billion trillion tonnes", then sneaky staccato pizzicato tiptoeing out the room!
    for m in [38, 50, 54, 57, 62, 66]:
        b.add("brass", I.brass(F(m), 1.4, 0.65, _r(), "soft", scoop=-8), 58.3, (m - 52) / 25.0)
    b.add("perc", I.timpani(F(38), 0.8, _r(), dur=2.2), 58.3, -0.1)
    b.add("bell", I.triangle(0.45, _r()), 58.3, 0.3)

    # Sneaky tiptoe pizzicato walk (62.5s -> dur)
    tiptoe = [62, 63, 62, 57, 58, 57, 53, 52, 50, 57, 62, 69, 74]
    for i, m in enumerate(tiptoe):
        tt_pos = 62.5 + i * 0.46
        if tt_pos >= dur - 0.3:
            break
        b.add("pluck", I.pluck(F(m), 0.82, _r(), dur=0.32, bright=0.8), tt_pos, -0.15 + 0.1 * (i % 3))
        b.add("counter", I.brush(0.4, _r(), dur=0.22), tt_pos, 0.15)
    # Final D minor/major wink button right before end
    end_t = max(62.5, dur - 0.9)
    b.add("pluck", I.pluck(F(50), 0.95, _r(), dur=0.7), end_t, -0.1)
    b.add("bell", I.musicbox(F(86), 0.65, _r(), dur=0.7), end_t, 0.2)
    return render_band(b, ref=-20.0)


def build_cavendish_sfx(dur: float, v_ref: float) -> np.ndarray:
    N = ns(dur)
    out = np.zeros((2, N))
    R = rng(1798)
    rr = lambda: rng(int(R.integers(1 << 30)))

    def add_ev(t, x, db_rel, p=0.0):
        x = pan(x, p) if np.ndim(x) == 1 else x
        cur = momentary_max(x)
        if np.isfinite(cur):
            x = x * dbg((v_ref + db_rel - 6.0) - cur)
        place(out, x, t)

    # Garden bird & breeze bed
    bed = G.breeze(dur, rr(), 0.75, 0.12, 750) + pan(G.bird_chirps(dur, rr(), 0.38, "blackbird") * 0.07, -0.45)
    cur_b = integrated(bed)
    if np.isfinite(cur_b):
        bed *= dbg((v_ref - 28.0) - cur_b)
    place(out, fades(bed, 0.4, 0.5), 0.0)

    # White flash whoosh at frame 130 (4.33s)
    add_ev(130.0 / 30.0 - 0.3, G.whoosh(0.7, rr(), 0.3, 450, 3800, 0.85, 0.1, 0.35), -5.0)

    # Giant 348-lb lead spheres heavy thud in Shot 4 (f455 = 15.17s)
    thud_t = tt(0.7)
    thud = np.exp(-thud_t / 0.16) * np.sin(phase(52 * (1 - 0.25 * thud_t))) * 2.5
    add_ev(15.15, thud, -5.0, -0.2)
    add_ev(15.15, G.clink(rr(), 950, 0.18), -9.0, -0.2)
    add_ev(15.55, thud, -5.5, 0.25)
    add_ev(15.55, G.clink(rr(), 950, 0.18), -9.5, 0.25)

    # Shed lock click & telescope brass slide in Shot 7 (24.5s)
    add_ev(24.2, G.clink(rr(), 2200, 0.14), -8.5, -0.2)
    add_ev(24.22, G.creak(0.35, rr(), 90, 160, G.WOOD), -9.0, -0.2)
    # Torsion wire subtle metallic ticks during Shot 7-8 (28.0s - 34.5s)
    for k in range(10):
        add_ev(28.2 + k * 0.6, G.clink(rr(), 3100 + k * 90, 0.09), -13.0, 0.15)
    # Camera transition whooshes
    for f_cut in [285, 445, 690, 985, 1310, 1640, 1880]:
        add_ev(f_cut / 30.0 - 0.08, G.whoosh(0.5, rr(), 0.08, 350, 1900, 0.8, 0.15, 0.15), -12.0)
    # Magnet click on steel board in Shot 12 (48.0s)
    add_ev(48.0, G.clink(rr(), 2800, 0.12), -8.0, 0.1)
    add_ev(48.02, G.push_thump(rr()), -9.5, 0.1)
    # Tiptoe footsteps in Shot 15 (62.8s -> end)
    for k in range(10):
        add_ev(62.8 + k * 0.46, G.stroll_step(rr(), 0.2), -11.0, -0.3 + 0.06 * k)
    return hp(out, 25, 2)


# ==============================================================================
# 2. MAGDEBURG SHORT (1654) - "Imperial Baroque Fanfare & Tug-of-War" (G major / E minor, 126 BPM)
# ==============================================================================
def build_magdeburg_music(dur: float) -> np.ndarray:
    N = ns(dur)
    b = EpBand(N)
    R = rng(1654)
    _r = lambda: rng(int(R.integers(1 << 30)))
    Q = 60.0 / 126.0  # 0.476s per beat
    FLASH = 130.0 / 30.0

    # Hook (0 -> 4.33s): Royal Baroque Brass Fanfare in G major + kettledrums
    fanfare = [(0.0, 0.35, 67), (0.38, 0.2, 71), (0.62, 0.2, 74), (0.88, 0.55, 79),
               (1.55, 0.3, 78), (1.9, 0.3, 79), (2.3, 0.7, 83)]
    for t, d, m in fanfare:
        b.add("lead", I.brass(F(m), d, 0.82, _r(), "horn", scoop=-14), t, -0.2)
        b.add("brass", I.brass(F(m - 12), d, 0.7, _r(), "tuba", scoop=-18), t, 0.15)
    for k in range(8):
        b.add("perc", I.timpani(F(43 if k % 2 == 0 else 38), 0.72, _r(), dur=0.6), k * 0.48, -0.1)
    # Button on white flash
    for m in [43, 55, 59, 62, 67, 74]:
        b.add("brass", I.brass(F(m), 0.28, 0.85, _r(), "stab", scoop=-12), FLASH, (m - 58) / 22.0)
    b.add("perc", I.cymbal(0.48, _r(), dur=1.2), FLASH, 0.0)

    # Story & Vacuum Pump (4.8s -> 18.8s): Bouncy Baroque Court Gavotte (fife + horns + tuba bass)
    gavotte_mel = [79, 78, 79, 74, 71, 74, 67, 71, 72, 71, 69, 67, 66, 69, 62, 66]
    for i, m in enumerate(gavotte_mel):
        t = 4.8 + i * (Q * 1.75)
        if t >= 18.8:
            break
        b.add("lead", I.fife(F(m), Q * 1.4, 0.68, _r()), t, 0.22)
        b.add("bell", I.glock(F(m + 12), 0.42, _r()), t, -0.28)
        b.add("bass", I.brass(F(43 if (i % 4) < 2 else 38), 0.32, 0.68, _r(), "tuba"), t, -0.1)
        b.add("brass", I.brass(F(55 if (i % 4) < 2 else 54), 0.18, 0.48, _r(), "horn"), t + Q * 0.85, 0.25)

    # 16 Warhorses Tug-of-War Escalation (18.8s -> 33.1s): Driving E minor galloping timpani + snare + heavy brass
    t_cur = 18.8
    step = 0
    while t_cur < 32.85:
        # Gallop rhythm: 8th + two 16ths
        b.add("perc", I.snare(0.65, _r()), t_cur, 0.08)
        b.add("perc", I.snare(0.45, _r()), t_cur + Q * 0.5, 0.08)
        b.add("perc", I.snare(0.52, _r()), t_cur + Q * 0.75, 0.08)
        if step % 2 == 0:
            root_m = [40, 43, 45, 47][(step // 2) % 4]
            b.add("bass", I.brass(F(root_m), 0.35, 0.82, _r(), "tuba"), t_cur, -0.1)
            b.add("perc", I.timpani(F(root_m), 0.78, _r(), dur=0.8), t_cur, -0.15)
            b.add("lead", I.brass(F(root_m + 24), 0.3, 0.74, _r(), "horn", scoop=-15), t_cur + Q * 0.5, -0.22)
        t_cur += Q
        step += 1
    # Dead stop at 33.0s as Guericke walks up with two fingers -> tiny brass valve turn -> POP!
    b.add("bell", I.triangle(0.65, _r()), 33.15, 0.1)
    for m in [43, 55, 59, 62, 67]:
        b.add("brass", I.brass(F(m), 0.45, 0.78, _r(), "stab"), 33.4, (m - 55) / 20.0)

    # Golden Hour Park Plunger Analogy (43.5s -> 58.0s): Playful pizzicato + vibraphone waltz in G major
    t_cur = 43.5
    bar = 0
    waltz_notes = [[79, 74, 71], [81, 76, 72], [79, 74, 67], [78, 74, 69]]
    waltz_bass = [43, 48, 43, 38]
    while t_cur < 58.0:
        ns_bar = waltz_notes[bar % 4]
        bm = waltz_bass[bar % 4]
        b.add("bass", I.pluck(F(bm), 0.85, _r(), dur=0.9), t_cur, -0.1)
        b.add("pad", I.pad([F(bm + 12), F(bm + 16), F(bm + 19)], 3 * Q, 0.38, _r()), t_cur, 0.0)
        for j, m in enumerate(ns_bar):
            b.add("lead", I.vibes(F(m), 0.62, _r(), dur=1.0, damp=0.6), t_cur + j * Q, -0.2)
            if j > 0:
                b.add("pluck", I.pluck(F(m - 12), 0.52, _r(), dur=0.45), t_cur + j * Q, 0.25)
        t_cur += 3 * Q
        bar += 1

    # Finale Triumph (58.0s -> dur): Imperial G major brass + fife celebration ("beaten by the weather")
    fin_notes = [67, 71, 74, 79, 83, 79, 74, 79]
    for i, m in enumerate(fin_notes):
        tt_pos = 58.2 + i * 0.82
        if tt_pos >= dur - 0.4:
            break
        b.add("lead", I.brass(F(m), 0.55, 0.75, _r(), "horn"), tt_pos, -0.2)
        b.add("counter", I.fife(F(m + 12), 0.5, 0.6, _r()), tt_pos, 0.25)
        b.add("bass", I.brass(F(43 if i % 2 == 0 else 38), 0.45, 0.78, _r(), "tuba"), tt_pos, -0.1)
    end_t = max(60.0, dur - 0.9)
    for m in [43, 50, 55, 59, 67, 79]:
        b.add("brass", I.brass(F(m), 0.65, 0.82, _r(), "stab"), end_t, 0.0)
    b.add("perc", I.cymbal(0.42, _r(), dur=1.0), end_t, 0.0)
    return render_band(b, ref=-20.0)


def build_magdeburg_sfx(dur: float, v_ref: float) -> np.ndarray:
    N = ns(dur)
    out = np.zeros((2, N))
    R = rng(1655)
    rr = lambda: rng(int(R.integers(1 << 30)))

    def add_ev(t, x, db_rel, p=0.0):
        x = pan(x, p) if np.ndim(x) == 1 else x
        cur = momentary_max(x)
        if np.isfinite(cur):
            x = x * dbg((v_ref + db_rel - 6.0) - cur)
        place(out, x, t)

    # Open plaza air + distant crowd murmur bed
    bed = G.breeze(dur, rr(), 0.85, 0.14, 820) + pan(G.bird_chirps(dur, rr(), 0.35, "sparrow") * 0.06, 0.4)
    cur_b = integrated(bed)
    if np.isfinite(cur_b):
        bed *= dbg((v_ref - 28.0) - cur_b)
    place(out, fades(bed, 0.4, 0.5), 0.0)

    # White flash at frame 130 (4.33s)
    add_ev(130.0 / 30.0 - 0.3, G.whoosh(0.7, rr(), 0.3, 450, 3800, 0.85, 0.1, 0.35), -5.0)

    # Copper bowls clank shut in Shot 3 (10.5s)
    clank = modal(0.45, [(420, 1.0, 0.12), (880, 0.7, 0.08), (1540, 0.4, 0.04)], rr())
    add_ev(10.5, clank, -6.0, 0.0)

    # Brass hand pump suction strokes in Shot 4 (14.8s -> 18.2s)
    for k in range(6):
        pump = G.whoosh(0.38, rr(), 0.18, 600, 2800, 0.7, 0.12, 0.3)
        add_ev(15.0 + k * 0.52, pump, -8.5, -0.25)
        add_ev(15.02 + k * 0.52, G.clink(rr(), 1900, 0.08), -11.0, -0.25)

    # Whip cracks, horse hooves & rope strain in Shots 5-7 (19.5s -> 32.5s)
    for k in range(3):
        whip_t = tt(0.18)
        whip = hp(rr().standard_normal(len(whip_t)), 1800) * np.exp(-whip_t / 0.004) * 2.2
        add_ev(20.2 + k * 3.8, whip, -5.5, -0.4 if k % 2 == 0 else 0.4)
    for k in range(18):
        add_ev(20.5 + k * 0.62, G.boot(rr(), 1.2), -10.5, -0.5 if k % 2 == 0 else 0.5)
    add_ev(26.0, G.creak(4.5, rr(), 65, 130, G.TIMBER, rough=0.2), -7.5, 0.0)

    # Shot 8 (33.15s): Tiny valve hiss + copper bowls pop apart!
    hiss_t = tt(0.45)
    hiss = bp(rr().standard_normal(len(hiss_t)), 2200, 7500, 1) * np.exp(-hiss_t / 0.15)
    pop = modal(0.55, [(380, 1.0, 0.18), (790, 0.8, 0.12), (1420, 0.5, 0.07)], rr())
    add_ev(33.1, hiss, -6.0, -0.1)
    add_ev(33.35, pop, -3.5, 0.0)

    # Rubber plunger suction thump in Shot 12 (48.2s)
    add_ev(48.2, G.push_thump(rr()), -6.5, 0.0)
    return hp(out, 25, 2)


# ==============================================================================
# 3. FARADAY SHORT (1836) - "Victorian Electric Scherzo" (A minor / C major, 132 BPM)
# ==============================================================================
def build_faraday_music(dur: float) -> np.ndarray:
    N = ns(dur)
    b = EpBand(N)
    R = rng(1836)
    _r = lambda: rng(int(R.integers(1 << 30)))
    Q = 60.0 / 132.0  # 0.4545s per beat
    FLASH = 130.0 / 30.0

    # Hook (0 -> 4.33s): Rapid electric A-minor arpeggios (glockenspiel + pizzicato + brass stabs)
    arp_am = [69, 72, 76, 81, 84, 81, 76, 72, 69, 72, 76, 81, 88, 84, 81, 76]
    for i, m in enumerate(arp_am):
        t = i * (FLASH / 16.0)
        b.add("spark", I.glock(F(m), 0.62, _r(), dur=0.45), t, -0.35 + 0.05 * i)
        if i % 2 == 0:
            b.add("pluck", I.pluck(F(m - 12), 0.78, _r(), dur=0.4, bright=0.8), t, 0.25)
    b.add("bass", I.brass(F(45), 0.6, 0.82, _r(), "tuba"), 0.0, -0.1)
    b.add("bass", I.brass(F(40), 0.6, 0.82, _r(), "tuba"), FLASH * 0.5, -0.1)
    # Flash lightning button
    for m in [45, 57, 60, 64, 69, 81]:
        b.add("brass", I.brass(F(m), 0.25, 0.88, _r(), "stab"), FLASH, 0.0)
    b.add("perc", I.cymbal(0.5, _r(), dur=1.1), FLASH, 0.0)

    # Lecture Hall & Generator Spin-up (4.8s -> 28.5s): Energetic Victorian Scherzo in A minor
    scherzo_ch = [
        ([57, 60, 64], 45, [81, 76, 72, 76]),  # Am
        ([53, 57, 60], 41, [77, 72, 69, 72]),  # F
        ([50, 53, 57], 38, [74, 69, 65, 69]),  # Dm
        ([52, 56, 59], 40, [76, 71, 68, 71]),  # E7
    ]
    t_cur = 4.8
    bar = 0
    while t_cur < 28.5:
        triad, bm, motif = scherzo_ch[bar % 4]
        b.add("bass", I.pluck(F(bm), 0.85, _r(), dur=0.7), t_cur, -0.1)
        b.add("bass", I.pluck(F(bm + 7), 0.72, _r(), dur=0.6), t_cur + 2 * Q, -0.1)
        b.add("pad", I.pad([F(m) for m in triad], 4 * Q, 0.36, _r(), att=0.2, rel=0.3), t_cur, 0.0)
        for k, m in enumerate(motif):
            b.add("pluck", I.pluck(F(m), 0.7, _r(), dur=0.42, bright=0.75), t_cur + k * Q, -0.25)
            b.add("spark", I.musicbox(F(m + 12), 0.52, _r(), dur=0.5), t_cur + k * Q + Q * 0.5, 0.3)
        if bar >= 3:
            b.add("perc", I.brush(0.45, _r(), dur=0.25), t_cur + Q, 0.1)
            b.add("perc", I.brush(0.45, _r(), dur=0.25), t_cur + 3 * Q, 0.1)
        t_cur += 4 * Q
        bar += 1

    # High-Voltage Charge Climb (28.5s -> 33.1s) -> Blinding Lightning Bolt Strike at 33.3s!
    for k in range(16):
        t = 28.5 + k * ((33.1 - 28.5) / 16.0)
        m = 69 + k
        b.add("spark", I.glock(F(m), 0.45 + 0.03 * k, _r(), dur=0.35), t, -0.4 + 0.05 * k)
        b.add("perc", I.snare(0.35 + 0.035 * k, _r(), buzz=True), t, 0.05)
    # 33.3s Strike + Calm gold leaf inside (crystalline celesta/vibes chord in pure Fmaj7 / Cmaj7)
    b.add("perc", I.timpani(F(33), 0.9, _r(), dur=2.4), 33.3, -0.1)
    b.add("perc", I.cymbal(0.55, _r(), dur=1.8), 33.3, 0.0)
    for k, m in enumerate([60, 64, 67, 71, 76, 84]):
        b.add("lead", I.vibes(F(m), 0.68, _r(), dur=2.4), 33.55 + k * 0.07, -0.25 + 0.1 * k)

    # Golden Hour Park Analogy: "People in a room who hate each other" (43.5s -> 58.0s)
    # Quirky staccato C-major / A-minor chamber conversation (fife + vibes + pizzicato)
    t_cur = 43.5
    bar = 0
    room_mel = [[72, 76, 79, 84], [74, 77, 81, 79], [76, 72, 69, 72], [71, 74, 79, 76]]
    room_bass = [48, 41, 45, 43]
    while t_cur < 58.0:
        mel = room_mel[bar % 4]
        bm = room_bass[bar % 4]
        b.add("bass", I.pluck(F(bm), 0.82, _r(), dur=0.8), t_cur, -0.1)
        b.add("pad", I.pad([F(bm + 12), F(bm + 16), F(bm + 19)], 4 * Q, 0.38, _r()), t_cur, 0.0)
        for k, m in enumerate(mel):
            b.add("lead", I.vibes(F(m), 0.6, _r(), dur=0.9, damp=0.5), t_cur + k * Q, -0.2)
            b.add("counter", I.fife(F(m), Q * 0.75, 0.48, _r()), t_cur + k * Q, 0.25)
        t_cur += 4 * Q
        bar += 1

    # Modern Faraday Cage & Airliner Peanuts Callback (58.0s -> dur): Bright C major swung vibes + brushes
    jazz_walk = [48, 52, 55, 57, 53, 57, 60, 55, 48, 55, 60, 48]
    for i, m in enumerate(jazz_walk):
        tt_pos = 58.2 + i * 0.68
        if tt_pos >= dur - 0.3:
            break
        b.add("bass", I.pluck(F(m), 0.85, _r(), dur=0.65), tt_pos, -0.1)
        b.add("lead", I.vibes(F(m + 24), 0.62, _r(), dur=0.8, damp=0.5), tt_pos, 0.2)
        b.add("perc", I.brush(0.45, _r(), dur=0.35, swish=True), tt_pos, 0.15)
    end_t = max(60.0, dur - 0.9)
    for m in [60, 64, 67, 71, 74]:
        b.add("lead", I.vibes(F(m), 0.65, _r(), dur=0.8), end_t, 0.15)
    b.add("spark", I.triangle(0.35, _r(), dur=0.6), end_t, 0.3)
    return render_band(b, ref=-20.0)


def build_faraday_sfx(dur: float, v_ref: float) -> np.ndarray:
    N = ns(dur)
    out = np.zeros((2, N))
    R = rng(1837)
    rr = lambda: rng(int(R.integers(1 << 30)))

    def add_ev(t, x, db_rel, p=0.0):
        x = pan(x, p) if np.ndim(x) == 1 else x
        cur = momentary_max(x)
        if np.isfinite(cur):
            x = x * dbg((v_ref + db_rel - 6.0) - cur)
        place(out, x, t)

    def zap_sound(r, d=0.28, big=False):
        t = tt(d)
        nz = r.standard_normal(len(t))
        crackle = bp(nz, 1400, 11000, 2) * np.exp(-t / (0.09 if big else 0.04)) * 1.8
        hum = np.sin(phase(120 * (1 + 0.15 * np.sin(TAU * 45 * t)))) * np.exp(-t / d) * 0.9
        if big:
            boom = np.exp(-t / 0.18) * np.sin(phase(68 * (1 + 0.5 * np.exp(-t / 0.02)))) * 2.6
            return fades(crackle + hum + boom, 0.001, 0.04)
        return fades(crackle + hum, 0.001, 0.02)

    # Lecture hall / plaza ambience bed
    bed = G.breeze(dur, rr(), 0.7, 0.1, 700)
    cur_b = integrated(bed)
    if np.isfinite(cur_b):
        bed *= dbg((v_ref - 29.0) - cur_b)
    place(out, fades(bed, 0.4, 0.5), 0.0)

    # Hook electric crackles + white flash (0 -> 4.33s)
    add_ev(1.2, zap_sound(rr(), 0.25, False), -6.5, -0.3)
    add_ev(2.6, zap_sound(rr(), 0.3, False), -6.0, -0.25)
    add_ev(130.0 / 30.0 - 0.1, zap_sound(rr(), 0.55, True), -4.0, 0.0)

    # Glass wheel spinning hum + electrostatic sparks in Shots 4-7 (15.0s -> 32.8s)
    wheel_whir = G.creak(6.0, rr(), 140, 220, G.SMALLMETAL, rough=0.05, noise=0.03)
    add_ev(15.2, wheel_whir, -11.0, -0.35)
    for tm in [16.4, 18.2, 20.8, 24.5, 27.2, 29.5, 31.2, 32.4]:
        add_ev(tm, zap_sound(rr(), 0.24, False), -6.5, -0.3)

    # Shot 8 (33.3s): Blinding blue bolt slams into the cage!
    add_ev(33.3, zap_sound(rr(), 0.75, True), -2.5, -0.15)
    # Complete silence / delicate glass chime inside for the unmoving gold leaf (34.4s)
    add_ev(34.4, I.glock(F(96), 0.5, rr(), dur=0.8), -9.0, 0.1)

    # Shuffling footsteps of people backing up to the walls in Shot 11-12 (44.5s -> 49.0s)
    for k in range(10):
        add_ev(44.5 + k * 0.42, G.stroll_step(rr(), 0.6), -11.0, -0.6 + 0.12 * k)
    return hp(out, 25, 2)


# Distinct episode configurations for the 6 new physics shorts (each with unique key, BPM, instruments, and physical SFX)
NEW_EPISODE_THEMES = {
    "GalileoShort": {
        "seed": 101, "bpm": 112.0, "root": 60, "mode": "renaissance",
        "prog": [(60, 64, 67), (57, 60, 64), (65, 69, 72), (67, 71, 74)],
        "lead": [72, 74, 76, 79, 76, 74, 72, 71, 69, 72, 74, 76, 74, 72, 71, 67],
        "inst": "flute_lute", "sfx": "cannonball",
    },
    "ArchimedesShort": {
        "seed": 202, "bpm": 126.0, "root": 62, "mode": "mediterranean",
        "prog": [(62, 65, 69), (60, 64, 67), (58, 62, 65), (60, 64, 67)],
        "lead": [74, 77, 76, 74, 72, 74, 77, 79, 77, 76, 74, 72, 70, 72, 74, 69],
        "inst": "lyre_perc", "sfx": "splash",
    },
    "NewtonShort": {
        "seed": 303, "bpm": 98.0, "root": 65, "mode": "pastoral",
        "prog": [(65, 69, 72), (62, 65, 69), (58, 62, 65), (60, 64, 67)],
        "lead": [77, 76, 74, 72, 74, 77, 79, 81, 79, 77, 74, 72, 70, 72, 74, 72],
        "inst": "cello_harp", "sfx": "apple",
    },
    "FranklinShort": {
        "seed": 404, "bpm": 120.0, "root": 64, "mode": "storm",
        "prog": [(64, 67, 71), (60, 64, 67), (62, 66, 69), (59, 62, 66)],
        "lead": [76, 79, 78, 76, 74, 76, 79, 83, 81, 79, 78, 76, 74, 71, 74, 76],
        "inst": "storm_brass", "sfx": "thunder",
    },
    "TeslaShort": {
        "seed": 505, "bpm": 132.0, "root": 59, "mode": "electric",
        "prog": [(59, 62, 66), (55, 59, 62), (57, 61, 64), (54, 57, 61)],
        "lead": [71, 74, 78, 83, 81, 78, 74, 71, 74, 78, 81, 86, 83, 81, 78, 74],
        "inst": "synth_arp", "sfx": "coil",
    },
    "RontgenShort": {
        "seed": 606, "bpm": 102.0, "root": 55, "mode": "xray",
        "prog": [(55, 58, 62), (51, 55, 58), (53, 57, 60), (50, 54, 57)],
        "lead": [79, 78, 79, 82, 81, 79, 77, 74, 79, 81, 82, 86, 84, 82, 81, 79],
        "inst": "glass_pad", "sfx": "xray_tube",
    },
    "PascalShort": {
        "seed": 707, "bpm": 116.0, "root": 60, "mode": "baroque",
        "prog": [(60, 63, 67), (58, 62, 65), (56, 60, 63), (55, 59, 62)],
        "lead": [72, 75, 79, 77, 75, 74, 72, 70, 72, 75, 77, 79, 77, 75, 74, 72],
        "inst": "cello_harp", "sfx": "splash",
    },
    "DopplerShort": {
        "seed": 808, "bpm": 128.0, "root": 62, "mode": "railroad",
        "prog": [(62, 66, 69), (59, 62, 66), (57, 61, 64), (59, 62, 66)],
        "lead": [74, 78, 81, 83, 81, 78, 76, 74, 78, 81, 85, 86, 85, 81, 78, 74],
        "inst": "storm_brass", "sfx": "cannonball",
    },
    "CurieShort": {
        "seed": 909, "bpm": 106.0, "root": 57, "mode": "radium",
        "prog": [(57, 60, 64), (53, 57, 60), (55, 59, 62), (52, 55, 59)],
        "lead": [76, 79, 81, 84, 83, 81, 79, 76, 77, 81, 83, 84, 83, 81, 79, 76],
        "inst": "glass_pad", "sfx": "xray_tube",
    },
}


def build_thematic_music(dur: float, cfg: dict) -> np.ndarray:
    b = EpBand(ns(dur))
    r_base = rng(cfg["seed"])
    r = lambda: rng(int(r_base.integers(1, 2**31 - 1)))
    beat = 60.0 / cfg["bpm"]
    n_beats = int(dur / beat)
    prog = cfg["prog"]
    lead = cfg["lead"]
    inst = cfg["inst"]

    for bi in range(n_beats):
        t = bi * beat
        bar = (bi // 4) % 4
        ch = prog[bar]
        note_m = lead[bi % len(lead)]

        # Bass pulse on downbeats
        if bi % 2 == 0:
            b.add("bass", I.brass(F(ch[0] - 24), beat * 1.6, 0.72, r(), kind="tuba"), t, p=-0.1, g=0.8)

        # Warm harmonic pad per bar
        if bi % 4 == 0:
            b.add("pad", I.pad([F(n_m) for n_m in ch], beat * 3.8, 0.45, r()), t, p=0.0, g=0.55)

        # Distinct lead + counter texture per episode genre
        if inst == "flute_lute":
            b.add("lead", I.fife(F(note_m), beat * 0.75, 0.62, r()), t, p=0.15, g=0.65)
            b.add("pluck", I.pluck(F(ch[bi % 3]), 0.6, r(), dur=beat * 0.8), t + beat * 0.5, p=-0.35, g=0.55)
        elif inst == "lyre_perc":
            b.add("pluck", I.pluck(F(note_m), 0.75, r(), dur=beat * 0.6, bright=0.7), t, p=0.2, g=0.75)
            b.add("perc", I.snare(0.55, r()), t, p=-0.25, g=0.45 if bi % 2 == 0 else 0.22)
        elif inst == "cello_harp":
            b.add("lead", I.brass(F(note_m - 12), beat * 1.1, 0.65, r(), kind="horn"), t, p=0.0, g=0.6)
            b.add("pluck", I.pluck(F(ch[(bi + 1) % 3] + 12), 0.55, r(), dur=beat * 0.7), t + beat * 0.5, p=0.35, g=0.5)
        elif inst == "storm_brass":
            if bi % 2 == 0:
                b.add("brass", I.brass(F(note_m - 12), beat * 1.3, 0.75, r(), kind="horn"), t, p=-0.2, g=0.7)
            b.add("perc", I.timpani(F(ch[0] - 24), 0.7, r()), t, p=0.15, g=0.55 if bi % 4 == 0 else 0.25)
        elif inst == "synth_arp":
            b.add("spark", I.vibes(F(note_m), 0.72, r(), dur=beat * 0.45), t, p=0.3 * math.sin(bi), g=0.75)
            b.add("pluck", I.musicbox(F(ch[bi % 3] + 12), 0.55, r(), dur=beat * 0.4), t + beat * 0.5, p=-0.3, g=0.6)
        else:  # glass_pad
            b.add("bell", I.vibes(F(note_m), 0.65, r(), dur=beat * 1.4), t, p=0.25, g=0.65)
            b.add("spark", I.glock(F(ch[bi % 3] + 24), 0.35, r(), dur=beat * 0.7), t + beat * 0.5, p=-0.25, g=0.45)

    return render_band(b, ref=-20.0)


def build_thematic_sfx(dur: float, v_ref: float, sfx_kind: str) -> np.ndarray:
    N = ns(dur)
    out = np.zeros((2, N))
    r = rng(777)
    rr = lambda: rng(int(r.integers(1, 2**31 - 1)))

    def add_ev(t: float, x: np.ndarray, rel: float = -6.0, p: float = 0.0):
        st_x = pan(x, p) if np.ndim(x) == 1 else x
        L = integrated(st_x)
        if np.isfinite(L):
            st_x = st_x * dbg((v_ref + rel) - L)
        place(out, st_x, t)

    # Subtle ambient bed
    bed = lp(colored(N, rr(), -1.5), 400.0) * 0.05
    place(out, fades(st(bed), 0.4, 0.5), 0.0)

    if sfx_kind == "cannonball":
        add_ev(4.5, G.hammer_hit(rr(), 1.1), -3.5, 0.0)   # Hook impact
        add_ev(33.9, G.hammer_hit(rr(), 1.5), -1.5, -0.15)  # Simultaneous cobblestone boom (S08)
        add_ev(33.92, G.hammer_hit(rr(), 1.0), -2.0, 0.15)
        add_ev(50.9, G.hammer_hit(rr(), 1.1), -3.0, 0.0)   # Bowling ball + marble hit (S12)
        add_ev(61.2, G.push_thump(rr()), -3.5, 0.0)        # Lunar hammer + feather landing (S14)
    elif sfx_kind == "splash":
        add_ev(5.5, G.push_thump(rr()), -4.5, 0.0)
        add_ev(29.5, G.splash_big(rr()), -2.5, 0.0)        # Tub water overflow (S07)
        add_ev(33.0, G.splash_big(rr()), -2.0, 0.0)        # Eureka leap (S08)
        add_ev(50.8, G.splash_big(rr()), -3.5, 0.1)        # Twin jars drop (S12)
        add_ev(55.5, G.splash_big(rr()), -2.5, 0.1)        # Crown dunk (S13)
    elif sfx_kind == "apple":
        add_ev(4.8, G.hammer_hit(rr(), 0.7), -4.5, 0.0)
        add_ev(16.0, G.push_thump(rr()), -2.5, 0.1)        # Apple bonk (S04)
        add_ev(33.0, G.whoosh(0.6, rr()), -3.0, 0.0)       # Mountain cannon blast (S08)
    elif sfx_kind == "thunder":
        add_ev(5.0, G.hammer_hit(rr(), 1.2), -3.5, 0.0)
        add_ev(16.5, G.hammer_hit(rr(), 1.3), -3.0, 0.0)   # Dark storm thunder (S04)
        add_ev(34.3, G.bolt_snap(rr()), -1.5, 0.0)         # Key-to-knuckle blue spark (S08)
        add_ev(53.2, G.bolt_snap(rr()), -3.0, 0.1)         # Carpet doorknob static zap (S12)
    elif sfx_kind == "coil":
        add_ev(5.5, I.vibes(F(88), 0.6, rr(), dur=0.4), -4.0, 0.0)
        add_ev(21.5, G.bolt_snap(rr()), -2.5, 0.0)         # Wardenclyffe arcs (S05)
        add_ev(44.0, G.hammer_hit(rr(), 1.4), -2.0, 0.0)   # Dynamite tower blast (S10)
        add_ev(52.5, I.glock(F(98), 0.8, rr(), dur=0.6), -3.5, 0.2)  # Tuning fork resonance (S12)
    else:  # xray_tube
        add_ev(5.3, I.glock(F(91), 0.5, rr(), dur=0.6), -5.0, 0.0)
        add_ev(19.3, I.vibes(F(84), 0.6, rr(), dur=0.6), -4.0, 0.0)  # X-ray screen reveal (S05)
        add_ev(33.7, I.vibes(F(86), 0.7, rr(), dur=0.9), -3.0, 0.0)  # Wedding ring plate (S08)
        add_ev(52.3, G.hammer_hit(rr(), 0.7), -3.5, 0.0)   # Marble fence bounce (S12)

    return hp(out, 25, 2)


def render_episode_score_and_sfx(comp: str, dur: float, v_ref: float) -> tuple[np.ndarray, np.ndarray]:
    if comp == "CavendishShort":
        return build_cavendish_music(dur), build_cavendish_sfx(dur, v_ref)
    if comp == "MagdeburgShort":
        return build_magdeburg_music(dur), build_magdeburg_sfx(dur, v_ref)
    if comp == "FaradayShort":
        return build_faraday_music(dur), build_faraday_sfx(dur, v_ref)
    if comp in NEW_EPISODE_THEMES:
        cfg = NEW_EPISODE_THEMES[comp]
        return build_thematic_music(dur, cfg), build_thematic_sfx(dur, v_ref, cfg["sfx"])
    # Default BridgeShort uses the original military march & bridge collapse SFX
    import music
    import sfx
    m_raw = music.render(music.build(), ref=-20.0)[0]
    s_raw = sfx.render(v_ref)[0]
    return m_raw, s_raw
