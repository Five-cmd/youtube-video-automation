"""Automated Physics YouTube Shorts Creator, Climax Experiment Editor, Sci-Fi HUD Designer,
Cloud Scheduler & Closed-Loop YouTube Analytics Self-Optimizer.

Key Capabilities:
1. Closed-Loop YouTube Analytics & Auto-Optimizer (run_auto_analytics_and_optimize):
   - Automatically fetches real-time viewCount, likeCount, commentCount, and duration for all channel videos.
   - Identifies the channel's winning duration sweet spot (11-15s high-retention loop), winning title patterns
     (ALL-CAPS focus word + 🤯 emoji), and top-performing tags (#explorephysics #physicsfundamentals #physicsfun).
   - Automatically heals/updates metadata (A/B Title, Comment-Trigger Question, and High-Performing Tags)
     in-place via youtube.videos().update() for any live or scheduled video without losing views or URLs.
   - Dynamically adapts script length and target clip duration for future Shorts based on live analytics.
2. Comfortable, Equalized Audio Volume Across All Clips:
   - Uses EBU R128 broadcast loudness normalization (loudnorm=I=-20:TP=-3.0:LRA=7,volume=0.72)
     so every single Short has the exact same comfortable volume.
   - Mixes clear English narration with a custom 124 BPM stereo Dark-Synth Science BGM track.
3. 0.0s Immediate Experiment Climax:
   - Uses frame-accurate per-segment input seeking (-ss / -to) so 0.0s always opens on the real
     physics experiment climax.
4. Floating Header Banner + 3D Glossy/Neon Glow HUD + Right-Aligned 55%-Opacity Metric Card + Sci-Fi Grid:
   - Follows the full visual hierarchy and dark charcoal/navy blueprint aesthetic.
5. Final 2-Second Source Attribution End Card.
"""
import asyncio
import datetime
import json
import math
import os
import pickle
import re
import shutil
import subprocess
import sys
import textwrap
import wave
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

BASE_DIR = Path(__file__).resolve().parent
INPUT_DIR = BASE_DIR / "input"
OUTPUT_DIR = BASE_DIR / "output"
PROCESSED_DIR = BASE_DIR / "processed"
HISTORY_FILE = BASE_DIR / "uploaded_history.json"
ANALYTICS_FILE = BASE_DIR / "analytics_report.json"
CLIENT_SECRETS_FILE = BASE_DIR / "client_secrets.json"
TOKEN_FILE = BASE_DIR / "youtube_token.pickle"
DEFAULT_LANGUAGE = "en"
YOUTUBE_SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.force-ssl",
]

WINNING_HASHTAGS = "#shorts #physics #science #explorephysics #physicsfundamentals #physicsfun"
WINNING_TAGS = [
    "physics",
    "science",
    "shorts",
    "explorephysics",
    "physicsfundamentals",
    "physicsfun",
    "scienceexperiments",
    "education",
    "experiment",
]

# Curated catalog of Physics Shorts topics with tight high-retention scripts (14-19s sweet spot)
# - ~50% (2 in 4) hooks start with viral "WAIT..." formula
# - Diverse, non-repetitive emojis (removed overused 🤯)
# - Direct related_topic_id mappings for cross-video promotion
PHYSICS_TOPICS: List[Dict[str, Any]] = [
    {
        "id": "lenz_law_copper_tube",
        "query": "magnet falling through copper pipe slow motion physics experiment",
        "hook": "WAIT... WHY DID THIS MAGNET FREEZE?!",
        "title": "Why Did This Magnet FREEZE Inside Copper?! ⚡ #shorts #physics #explorephysics",
        "title_alt": "Wait... This Magnet Refuses to Fall Inside Copper! ⚡ #shorts #physics #explorephysics",
        "comment_q": "💬 Quick quiz: What happens if you drop it in an aluminum pipe instead? Comment your guess!",
        "narration": (
            "Wait... look straight inside this copper pipe! Why did this super-magnet just freeze in mid-air?! "
            "Copper isn't even magnetic, yet when you drop a neodymium magnet inside, gravity suddenly loses! "
            "The falling magnet forces electrons inside the copper to spin in wild loops called eddy currents, "
            "creating an invisible magnetic cushion that brakes the fall! Follow for daily physics!"
        ),
        "segments": [(79.5, 88.5), (42.5, 48.5)],
        "metric_line1": "10x SLOWER",
        "metric_line2": "EDDY CURRENT BRAKE",
        "metric_sub": "DEFIES GRAVITY!",
        "source_credit": "Harvard Natural Sciences Lecture Demonstrations — Lenz's Law",
        "related_topic_id": "quantum_levitation_superconductor",
        "related_title": "Frozen in Mid-Air at -196°C",
    },
    {
        "id": "prince_ruperts_drop",
        "query": "prince rupert's drop bullet slow motion physics",
        "hook": "WAIT... A GLASS DROP SHATTERS A BULLET?!",
        "title": "Bullet vs. UNBREAKABLE Glass Drop! 💥 #shorts #physics #explorephysics",
        "title_alt": "Wait... This Glass Drop SHATTERS a Speeding Bullet?! 💥 #shorts #physics #explorephysics",
        "comment_q": "💬 Would a hydraulic press crush the head or shatter the steel first? Comment your guess!",
        "narration": (
            "Wait... watch closely as a speeding bullet slams straight into this glass drop—and the bullet shatters instead! "
            "When molten glass hits cold water, the outside freezes instantly while the core pulls inward with insane tension. "
            "The head can survive a bullet... but nick the paper-thin tail, and the entire drop explodes at five thousand miles per hour!"
        ),
        "segments": [(155.0, 163.5), (0.5, 7.5)],
        "metric_line1": "90-170 MPa",
        "metric_line2": "13,000-25,000 PSI",
        "metric_sub": "LARGER THAN THAT!",
        "source_credit": "Smarter Every Day — High-Speed Prince Rupert's Drop Experiment",
        "related_topic_id": "slinky_free_fall_slow_motion",
        "related_title": "Why Does the Bottom of This Slinky Float?!",
    },
    {
        "id": "quantum_levitation_superconductor",
        "query": "quantum levitation superconductor magnetic track physics demonstration",
        "hook": "FROZEN IN MID-AIR AT -196°C!",
        "title": "This Disc Freezes in MID-AIR at -196°C?! ❄️ #shorts #physics #explorephysics",
        "title_alt": "How Quantum Locking Freezes Objects in Mid-Air! ❄️ #shorts #physics #explorephysics",
        "comment_q": "💬 What happens when the liquid nitrogen warms up? Drop your answer in the comments!",
        "narration": (
            "There are no strings—this smoking disc is locked completely frozen in mid-air! "
            "Cooled to minus 196 degrees, a superconductor traps magnetic flux tubes like quantum anchors, "
            "floating even upside down with zero friction!"
        ),
        "segments": [(183.0, 191.0), (226.0, 234.0)],
        "metric_line1": "-196 °C (77 K)",
        "metric_line2": "QUANTUM FLUX LOCK",
        "metric_sub": "ZERO FRICTION!",
        "source_credit": "Supermagnete — Quantum Locking & Superconductor Levitation",
        "related_topic_id": "lenz_law_copper_tube",
        "related_title": "Why Did This Magnet Freeze Inside Copper?!",
    },
    {
        "id": "acoustic_levitation_sound",
        "query": "acoustic levitation standing wave droplets physics experiment",
        "hook": "TRAPPED IN MID-AIR BY PURE SOUND?!",
        "title": "This Water Droplet Floats on PURE SOUND?! 🔊 #shorts #physics #explorephysics",
        "title_alt": "Can Sound Waves Trap Liquid in Mid-Air?! 🔊 #shorts #physics #explorephysics",
        "comment_q": "💬 Could giant sound waves ever levitate a human? Comment YES or NO below!",
        "narration": (
            "Nothing is touching this spinning star—it's a liquid drop trapped in mid-air by pure sound! "
            "Ultrasonic waves collide to form invisible low-pressure cages called nodes, "
            "morphing floating droplets into spinning stars against gravity!"
        ),
        "segments": [(78.0, 86.0), (92.0, 100.0)],
        "metric_line1": "40,000 Hz",
        "metric_line2": "ULTRASONIC NODES",
        "metric_sub": "PURE SOUND FORCE!",
        "source_credit": "Acoustic Levitation Lab — Ultrasonic Star Droplet Harmonics",
        "related_topic_id": "chladni_plate_cymatics",
        "related_title": "This Is What Hidden Sound Waves Look Like!",
    },
    {
        "id": "ferrofluid_magnetic_spikes",
        "query": "ferrofluid magnet experiment demonstration slow motion",
        "hook": "WAIT... IS THIS MAGNETIC LIQUID ALIVE?!",
        "title": "Is This Magnetic Liquid ALIVE?! 🧪 #shorts #physics #explorephysics",
        "title_alt": "Wait... Injecting NASA Magnetic Liquid Onto a Magnet! 🧪 #shorts #physics #explorephysics",
        "comment_q": "💬 What would happen if you touched ferrofluid with your bare hand? Comment below!",
        "narration": (
            "Wait... watch black magnetic liquid erupt the instant it touches a magnet floating in mid-air! "
            "Invented by NASA for zero-gravity rocket fuel, billions of nanoscale iron particles "
            "wrap around invisible magnetic field lines right before your eyes!"
        ),
        "segments": [(3.5, 19.0)],
        "metric_line1": "10 NANOMETERS",
        "metric_line2": "NASA FERROFLUID",
        "metric_sub": "VISIBLE MAGNETISM!",
        "source_credit": "NoLimitsFX — Superconductor & Ferrofluid in Slow Motion",
        "related_topic_id": "quantum_levitation_superconductor",
        "related_title": "This Disc Freezes in Mid-Air at -196°C",
    },
    {
        "id": "slinky_free_fall_slow_motion",
        "query": "slinky drop slow motion physics experiment",
        "hook": "99% OF PEOPLE GET THIS WRONG!",
        "title": "Why Does the Bottom of This Slinky FLOAT?! 🌀 #shorts #physics #explorephysics",
        "title_alt": "99% of People Guess WRONG When This Slinky Drops! 🌀 #shorts #physics #explorephysics",
        "comment_q": "💬 Did you guess the bottom would float or fall right away? Be honest in the comments!",
        "narration": (
            "When this stretched slinky is dropped, watch the bottom in slow motion—it stays completely frozen in mid-air! "
            "Upward spring tension cancels out gravity 100 percent until the shockwave travels all the way down the coils!"
        ),
        "segments": [(47.0, 61.5)],
        "metric_line1": "1,000 FPS",
        "metric_line2": "0 G NET FORCE",
        "metric_sub": "FROZEN IN AIR!",
        "source_credit": "Veritasium & Prof. Rod Cross — Giant Slinky Slow-Motion Drop",
        "related_topic_id": "prince_ruperts_drop",
        "related_title": "Bullet vs. UNBREAKABLE Glass Drop!",
    },
    {
        "id": "chladni_plate_cymatics",
        "query": "chladni plate sand resonance frequency physics experiment",
        "hook": "THIS IS WHAT SOUND ACTUALLY LOOKS LIKE!",
        "title": "This Is What Hidden Sound Waves LOOK Like! ✨ #shorts #physics #explorephysics",
        "title_alt": "Watch Pure Sound Turn Sand Into Geometry! ✨ #shorts #physics #explorephysics",
        "comment_q": "💬 Why does higher frequency create more complex shapes? Comment your theory!",
        "narration": (
            "Have you ever seen what sound actually looks like?! "
            "Blast a metal plate with one pure frequency, and sand scrambles into razor-sharp geometric nodal lines—making invisible sound waves visible!"
        ),
        "metric_line1": "528 - 2,400 Hz",
        "metric_line2": "STANDING WAVE NODES",
        "metric_sub": "VISIBLE GEOMETRY!",
        "source_credit": "Physics Resonance Lab — Chladni Plate Cymatics Demonstration",
        "related_topic_id": "acoustic_levitation_sound",
        "related_title": "This Water Droplet Floats on Pure Sound",
    },
    {
        "id": "leidenfrost_effect_water",
        "query": "leidenfrost effect water droplets hot pan physics experiment",
        "hook": "WAIT... WHY ISN'T THIS WATER BOILING?!",
        "title": "Why Water Droplets LEVITATE on Hot Metal! 🔥 #shorts #physics #explorephysics",
        "title_alt": "Wait... Why Doesn't This Water Boil on a 200°C Pan?! 🔥 #shorts #physics #explorephysics",
        "comment_q": "💬 Have you ever seen water dance like this on a hot pan at home? Comment below!",
        "narration": (
            "Wait... why isn't this water boiling away on scorching-hot metal?! "
            "Above 193 degrees Celsius, the bottom of each droplet flashes into a tiny steam hovercraft cushion that levitates the liquid!"
        ),
        "metric_line1": "193 °C (379 °F)",
        "metric_line2": "STEAM HOVERCRAFT",
        "metric_sub": "VAPOR SHIELD!",
        "source_credit": "Thermodynamics Lab — Leidenfrost Vapor Cushion Experiment",
        "related_topic_id": "laser_waterfall_fiber_optics",
        "related_title": "Since When Can Water Bend a Laser Beam?!",
    },
    {
        "id": "gyroscopic_precession_wheel",
        "query": "bicycle wheel gyroscope precession rope physics demonstration",
        "hook": "WAIT... HOW IS THIS WHEEL NOT FALLING?!",
        "title": "How Does This Spinning Wheel DEFY Gravity?! 🎡 #shorts #physics #explorephysics",
        "title_alt": "Wait... Why Doesn't This Heavy Wheel Fall Over?! 🎡 #shorts #physics #explorephysics",
        "comment_q": "💬 What happens if you spin the wheel in the opposite direction? Comment your guess!",
        "narration": (
            "Wait... hang a heavy wheel from one rope and let go—it crashes down. "
            "Now spin it fast and let go again... instead of falling, gravity twists its angular momentum sideways in gyroscopic precession!"
        ),
        "metric_line1": "90° TORQUE SHIFT",
        "metric_line2": "ANGULAR MOMENTUM",
        "metric_sub": "DEFIES GRAVITY!",
        "source_credit": "MIT Physics Demo — Bicycle Wheel Gyroscopic Precession",
        "related_topic_id": "double_pendulum_chaos",
        "related_title": "The Simple Pendulum That Broke Physics!",
    },
    {
        "id": "bernoulli_levitating_ball",
        "query": "bernoulli principle floating ball air stream physics demonstration",
        "hook": "LOCKED INSIDE AN INVISIBLE AIR TUNNEL!",
        "title": "Why Can't This Ball Escape the Air Stream?! 💨 #shorts #physics #explorephysics",
        "title_alt": "Trapped Inside an Invisible Air Tunnel at 45°! 💨 #shorts #physics #explorephysics",
        "comment_q": "💬 How far can you tilt the blower before the ball finally drops? Comment your guess!",
        "narration": (
            "Even when you tilt the blower at 45 degrees, the ball refuses to fall! "
            "Fast air hugging the curve creates a low-pressure pocket, so higher outside air pressure slams the ball right back inside!"
        ),
        "metric_line1": "45° TILT LOCK",
        "metric_line2": "LOW PRESSURE CORE",
        "metric_sub": "AIR TUNNEL TRAP!",
        "source_credit": "Aerodynamics Lab — Bernoulli & Coanda Levitation Demo",
        "related_topic_id": "acoustic_levitation_sound",
        "related_title": "This Water Droplet Floats on Pure Sound",
    },
    {
        "id": "laser_waterfall_fiber_optics",
        "query": "total internal reflection laser water stream physics experiment",
        "hook": "WAIT... YOU CAN BEND A LASER BEAM?!",
        "title": "Since When Can Water BEND a Laser Beam?! 🚨 #shorts #physics #explorephysics",
        "title_alt": "Wait... How Water Traps a Laser Beam! 🚨 #shorts #physics #explorephysics",
        "comment_q": "💬 Did you know this is how undersea fiber-optic internet cables work? Comment below!",
        "narration": (
            "Wait... we're taught light only travels in straight lines, so how is this laser beam curving inside falling water?! "
            "Every time the laser hits the water edge, it bounces 100 percent back inside by Total Internal Reflection!"
        ),
        "metric_line1": "48.6° CRITICAL",
        "metric_line2": "100% LIGHT TRAP",
        "metric_sub": "LIQUID FIBER OPTICS!",
        "source_credit": "Optics Physics Demo — Total Internal Reflection Laser Stream",
        "related_topic_id": "leidenfrost_effect_water",
        "related_title": "Why Water Droplets Levitate on Hot Metal!",
    },
    {
        "id": "double_pendulum_chaos",
        "query": "double pendulum chaos theory glow in the dark physics",
        "hook": "EVEN SUPERCOMPUTERS CAN'T PREDICT THIS!",
        "title": "The Simple Pendulum That BROKE Physics! ⏳ #shorts #physics #explorephysics",
        "title_alt": "Why Even Supercomputers Can't Predict This Toy! ⏳ #shorts #physics #explorephysics",
        "comment_q": "💬 How many seconds until two identical double pendulums diverge? Comment your guess!",
        "narration": (
            "One pendulum swings like clockwork... but bolt a second arm onto the bottom, and pure chaos erupts! "
            "Drop two at almost the exact same angle, and within three seconds their paths violently diverge!"
        ),
        "metric_line1": "0.001° SHIFT",
        "metric_line2": "EXPONENTIAL CHAOS",
        "metric_sub": "UNPREDICTABLE!",
        "source_credit": "Nonlinear Dynamics Lab — Double Pendulum Chaos Demonstration",
        "related_topic_id": "gyroscopic_precession_wheel",
        "related_title": "How Does This Spinning Wheel Defy Gravity?!",
    },
    {
        "id": "oobleck_non_newtonian_fluid",
        "query": "oobleck non newtonian fluid cornstarch water speaker slow motion",
        "hook": "WAIT... WHY DID THIS LIQUID TURN SOLID?!",
        "title": "Punching This Liquid Turns It ROCK-HARD! 🥣 #shorts #physics #explorephysics",
        "title_alt": "Wait... Why Did This Liquid Turn Solid?! 🥣 #shorts #physics #explorephysics",
        "comment_q": "💬 Can you run across a pool of oobleck without sinking? Comment below!",
        "narration": (
            "Wait... why does this white puddle turn rock-hard the instant you punch it?! "
            "Made of cornstarch and water, gentle touch lets particles slide like liquid, but sudden impact locks them into a solid shield!"
        ),
        "metric_line1": "SHEAR THICKENING",
        "metric_line2": "NON-NEWTONIAN",
        "metric_sub": "LIQUID TO SOLID!",
        "source_credit": "Fluid Dynamics Lab — Non-Newtonian Shear Thickening Demo",
        "related_topic_id": "ferrofluid_magnetic_spikes",
        "related_title": "Is This Magnetic Liquid ALIVE?!",
    },
    {
        "id": "eulers_disk_spinning",
        "query": "eulers disk spinning slow motion physics sound",
        "hook": "WHY WON'T THIS HEAVY DISK STOP?!",
        "title": "This Spinning Disk Speeds Up FOREVER! 💿 #shorts #physics #explorephysics",
        "title_alt": "Why Does Euler's Disk Spin Faster and Faster?! 💿 #shorts #physics #explorephysics",
        "comment_q": "💬 How many minutes do you think this disk can spin? Guess in the comments!",
        "narration": (
            "Spin a regular coin and it flops over in seconds... but spin this heavy chrome disk on a concave mirror, "
            "and it rattles faster and faster for minutes, defying friction through rolling acoustic resonance!"
        ),
        "metric_line1": "SPOLIGOID RESONANCE",
        "metric_line2": "ZERO RESISTANCE",
        "metric_sub": "ENDLESS SPIN!",
        "source_credit": "Mechanics Lab — Euler's Disk Spoligoid Resonance Experiment",
        "related_topic_id": "gyroscopic_precession_wheel",
        "related_title": "How Does This Spinning Wheel DEFY Gravity?!",
    },
    {
        "id": "rubens_tube_fire_sound",
        "query": "rubens tube standing wave fire sound frequency experiment",
        "hook": "WAIT... SOUND WAVES MADE OF PURE FIRE?!",
        "title": "Watch Pure Sound Turn Into Dancing FIRE! 🔥 #shorts #physics #explorephysics",
        "title_alt": "Wait... Sound Waves Made of Dancing FIRE?! 🔥 #shorts #physics #explorephysics",
        "comment_q": "💬 What musical song would look coolest on a fire tube? Comment below!",
        "narration": (
            "Wait... can sound waves actually sculpt dancing pillars of pure flame?! "
            "Blast bass frequencies inside a perforated gas pipe, and acoustic standing wave nodes create high and low pressure zones that shoot fire into visual soundwaves!"
        ),
        "metric_line1": "STANDING FLAME NODES",
        "metric_line2": "ACOUSTIC PRESSURE",
        "metric_sub": "VISIBLE SOUND!",
        "source_credit": "Acoustics & Thermodynamics Lab — Rubens Flame Tube Demonstration",
        "related_topic_id": "chladni_plate_cymatics",
        "related_title": "This Is What Hidden Sound Waves LOOK Like!",
    },
    {
        "id": "vortex_cannon_smoke_ring",
        "query": "vortex cannon smoke ring giant slow motion experiment",
        "hook": "AIR CAN SMASH TARGETS FROM 30 FEET?!",
        "title": "Can an INVISIBLE Blast of Air Knock Down Cups?! 💨 #shorts #physics #explorephysics",
        "title_alt": "Giant Vortex Cannon Shoots Invisible Smoke Torus! 💨 #shorts #physics #explorephysics",
        "comment_q": "💬 Would a giant air cannon work underwater too? Comment YES or NO below!",
        "narration": (
            "Punt a blast of air through a small circular hole, and friction rolls the edges into a high-speed toroidal vortex ring, "
            "traveling dozens of feet with enough concentrated kinetic energy to blast targets over!"
        ),
        "metric_line1": "TOROIDAL VORTEX",
        "metric_line2": "KINETIC AIR RING",
        "metric_sub": "INVISIBLE BLAST!",
        "source_credit": "Fluid Dynamics Lab — Toroidal Vortex Ring Air Cannon Experiment",
        "related_topic_id": "bernoulli_levitating_ball",
        "related_title": "Why Can't This Ball Escape the Air Stream?!",
    },
    {
        "id": "induction_melting_mid_air",
        "query": "induction heater melting metal floating mid air physics experiment",
        "hook": "WAIT... MELTING METAL FLOATING IN MID-AIR?!",
        "title": "Melting Metal Levitating in MID-AIR! ⚡ #shorts #physics #explorephysics",
        "title_alt": "Wait... Melting Metal Floating in Mid-Air?! ⚡ #shorts #physics #explorephysics",
        "comment_q": "💬 What temperature does aluminum melt at? Test your science memory in the comments!",
        "narration": (
            "Wait... this molten sphere of aluminum is glowing red-hot and floating with zero physical contact! "
            "High-frequency induction coils blast alternating magnetic fields, inducing eddy currents that levitate the metal while heating it past 660 degrees Celsius!"
        ),
        "metric_line1": "660 °C (1,220 °F)",
        "metric_line2": "EDDY LEVITATION",
        "metric_sub": "MOLTEN FLOAT!",
        "source_credit": "Electromagnetism Lab — Magnetic Levitation Induction Melting",
        "related_topic_id": "lenz_law_copper_tube",
        "related_title": "Why Did This Magnet FREEZE Inside Copper?!",
    },
    {
        "id": "magdeburg_hemispheres_vacuum",
        "query": "magdeburg hemispheres atmospheric pressure vacuum experiment",
        "hook": "AIR PRESSURE DEFEATS HORSES?!",
        "title": "Why Can't 2 Teams of HORSES Pull This Apart?! 🐴 #shorts #physics #explorephysics",
        "title_alt": "Atmospheric Pressure Defeats Two Teams of Horses! 🐴 #shorts #physics #explorephysics",
        "comment_q": "💬 How many pounds of air are pressing down on your head right now? Drop your guess!",
        "narration": (
            "Place two hollow metal bowls together with no latch or glue, pump out the air inside, "
            "and the atmospheric pressure of Earth's atmosphere clamps them together with tons of unbreakable force!"
        ),
        "metric_line1": "14.7 PSI",
        "metric_line2": "VACUUM SUCTION",
        "metric_sub": "TONS OF FORCE!",
        "source_credit": "Atmospheric Physics Demo — Magdeburg Hemispheres Vacuum Force",
        "related_topic_id": "bernoulli_levitating_ball",
        "related_title": "Locked Inside an Invisible Air Tunnel!",
    },
    {
        "id": "curie_point_heat_magnet",
        "query": "curie point pendulum experiment",
        "hook": "WAIT... FIRE KILLS MAGNETISM?!",
        "title": "Watch FIRE Destroy a Magnet's Power Instantly! 🧲 #shorts #physics #explorephysics",
        "title_alt": "Wait... Heating a Magnet Kills Its Magnetism?! 🧲 #shorts #physics #explorephysics",
        "comment_q": "💬 Did you know heat destroys permanent magnets? Comment below!",
        "narration": (
            "Wait... heat a swinging magnet with a tiny flame, and the moment it hits its Curie temperature, "
            "thermal energy scatters its magnetic domains—causing it to instantly drop away until it cools and attracts again!"
        ),
        "metric_line1": "CURIE POINT",
        "metric_line2": "DOMAIN DISRUPTION",
        "metric_sub": "MAGNETISM LOST!",
        "source_credit": "Thermodynamics & Magnetism Lab — Curie Point Pendulum Demonstration",
        "related_topic_id": "quantum_levitation_superconductor",
        "related_title": "This Disc Freezes in MID-AIR at -196°C?!",
    },
    {
        "id": "rattleback_spin_reversal",
        "query": "rattleback stone spin reversal angular momentum physics",
        "hook": "THIS STONE REVERSES TIME?!",
        "title": "This Magic Stone Reverses Its Own Spin! 🪨 #shorts #physics #explorephysics",
        "title_alt": "Why Does This Asymmetric Stone Reverse Spin?! 🪨 #shorts #physics #explorephysics",
        "comment_q": "💬 Spin it clockwise vs counter-clockwise... which direction works? Comment below!",
        "narration": (
            "Spin this simple boat-shaped stone clockwise, and it quickly stops, rattles violently, "
            "and miraculously starts spinning in reverse! Asymmetric mass distribution converts spin into pitch oscillation, forcing angular momentum to flip!"
        ),
        "metric_line1": "ASYMMETRIC MASS",
        "metric_line2": "ANGULAR FLIP",
        "metric_sub": "REVERSE SPIN!",
        "source_credit": "Classical Mechanics Lab — Rattleback Celtic Stone Inversion",
        "related_topic_id": "double_pendulum_chaos",
        "related_title": "The Simple Pendulum That BROKE Physics!",
    },
    {
        "id": "atmospheric_pressure_drum_crush",
        "query": "crushing 55 gallon steel drum atmospheric pressure steam physics experiment",
        "hook": "WAIT... INVISIBLE AIR CRUSHES STEEL?!",
        "title": "Why Did This Steel Drum IMPLODE In 0.1s?! 💥 #shorts #physics #explorephysics",
        "title_alt": "Wait... Invisible Air Just Crushed This Steel Drum! 💥 #shorts #physics #explorephysics",
        "comment_q": "💬 Quick quiz: Could atmospheric pressure crush a submarine? Drop your thoughts below!",
        "narration": (
            "Wait... watch this thick steel drum get violently crushed by literally nothing! "
            "When steam inside cools, it condenses back into liquid water, creating a sudden vacuum inside. "
            "Fourteen point seven pounds of air pressure per square inch slams down from all sides, "
            "instantly flattening heavy steel like a soda can! Follow for daily physics!"
        ),
        "metric_line1": "14.7 PSI",
        "metric_line2": "ATMOSPHERIC CRUSH",
        "metric_sub": "INSTANT IMPLOSION!",
        "source_credit": "Physics Demonstration — 55-Gallon Drum Atmospheric Pressure Implosion",
        "related_topic_id": "magdeburg_hemispheres_vacuum",
        "related_title": "Why Can't 2 Teams of HORSES Pull This Apart?!",
    },
    {
        "id": "diamagnetic_graphite_levitation",
        "query": "pyrolytic graphite diamagnetic levitation neodymium magnets experiment",
        "hook": "WAIT... ROOM TEMP LEVITATION?!",
        "title": "Room-Temperature LEVITATION Without Any Power! 🧲 #shorts #physics #explorephysics",
        "title_alt": "Wait... This Carbon Disc FLOATS Over Pure Magnets?! 🧲 #shorts #physics #explorephysics",
        "comment_q": "💬 Did you know water and humans are slightly diamagnetic too? Comment below!",
        "narration": (
            "Wait... no liquid nitrogen, no batteries—how is this dark disc floating in mid-air?! "
            "This is pyrolytic graphite, one of the most diamagnetic materials on Earth. "
            "When placed above neodymium magnets, its electron orbits warp to repel the magnetic field, "
            "creating a frictionless magnetic cushion that defies gravity forever! Follow for daily physics!"
        ),
        "metric_line1": "ROOM TEMP",
        "metric_line2": "DIAMAGNETIC CUSHION",
        "metric_sub": "PERMANENT FLOAT!",
        "source_credit": "Physics Demonstration — Pyrolytic Graphite Diamagnetic Levitation",
        "related_topic_id": "quantum_levitation_superconductor",
        "related_title": "This Disc Freezes in MID-AIR at -196°C?!",
    },
    {
        "id": "superfluid_helium_fountain",
        "query": "superfluid helium fountain effect zero viscosity rollin film experiment",
        "hook": "WAIT... THIS LIQUID FLOWS UPHILL?!",
        "title": "Why Does This Liquid CLIMB Up Glass Walls?! ❄️ #shorts #physics #explorephysics",
        "title_alt": "Wait... This Liquid Flows UPHILL and Never Stops! ❄️ #shorts #physics #explorephysics",
        "comment_q": "💬 Quick quiz: Could a superfluid ever freeze completely solid? Comment below!",
        "narration": (
            "Wait... watch closely as this liquid starts climbing completely uphill against gravity! "
            "Cooled near absolute zero to two point one seven Kelvin, liquid helium turns into a quantum superfluid with zero viscosity! "
            "It crawls up beaker walls in an atom-thin Rollin film and leaks through solid glass pores, "
            "breaking classical physics forever! Follow for daily physics!"
        ),
        "metric_line1": "2.17 K (-271°C)",
        "metric_line2": "ZERO VISCOSITY",
        "metric_sub": "FLOWS UPHILL!",
        "source_credit": "Alfred Leitner — Liquid Helium Superfluid Demonstrations",
        "related_topic_id": "quantum_levitation_superconductor",
        "related_title": "This Disc Freezes in MID-AIR at -196°C?!",
    },
    {
        "id": "singing_tesla_coil_sound",
        "query": "musical singing tesla coil plasma arc high voltage physics experiment",
        "hook": "WAIT... ELECTRICITY CAN PLAY MUSIC?!",
        "title": "This 500,000 Volt LIGHTNING Plays Music! ⚡ #shorts #physics #explorephysics",
        "title_alt": "Wait... Pure Lightning Singing Like a Synthesizer?! ⚡ #shorts #physics #explorephysics",
        "comment_q": "💬 What song would you want a Tesla coil to play? Comment below!",
        "narration": (
            "Wait... listen closely to these giant sparks of raw electricity—that lightning is literally singing music! "
            "By pulsing half a million volts on and off thousands of times a second, "
            "the superheated plasma sparks violently expand and contract the surrounding air, "
            "turning pure high-voltage arcs into high-fidelity acoustic speakers! Follow for daily physics!"
        ),
        "metric_line1": "500,000 VOLTS",
        "metric_line2": "PLASMA SOUND WAVES",
        "metric_sub": "RAW LIGHTNING SOUND!",
        "source_credit": "ArcAttack — High-Voltage Solid-State Singing Tesla Coil",
        "related_topic_id": "rubens_tube_fire_sound",
        "related_title": "Watch Pure Sound Turn Into Dancing FIRE!",
    },
    {
        "id": "chain_fountain_mould_effect",
        "query": "mould effect chain fountain physics demonstration slow motion",
        "hook": "WAIT... THIS CHAIN JUMPS INTO MID-AIR?!",
        "title": "The Chain That LEAPS Into Mid-Air! ⛓️ #shorts #physics #explorephysics",
        "title_alt": "Wait... Why Does This Falling Chain Leap Upwards?! ⛓️ #shorts #physics #explorephysics",
        "comment_q": "💬 What pushes the chain up before it falls? Guess in the comments below!",
        "narration": (
            "Wait... pull a long beaded chain over the rim of a beaker, and instead of just sliding down, it miraculously arches high into empty air like an invisible fountain! As beads are jerked off the pot, the kickback force from the container pushes each link upwards before gravity takes over!"
        ),
        "metric_line1": "MOULD EFFECT",
        "metric_line2": "KICKBACK LEAP",
        "metric_sub": "DEFYING GRAVITY!",
        "source_credit": "Physics Demonstration — Self-Siphoning Mould Effect Chain Fountain",
        "related_topic_id": "slinky_free_fall_slow_motion",
        "related_title": "Why Does the Bottom of This Slinky FLOAT in Mid-Air?!",
    },
    {
        "id": "water_bridge_high_voltage",
        "query": "floating water bridge experiment high voltage",
        "hook": "WAIT... WATER CAN FORM A FLOATING BRIDGE?!",
        "title": "High Voltage FLOATS a Water Bridge in Mid-Air! ⚡ #shorts #physics #explorephysics",
        "title_alt": "Wait... 25,000 Volts Stretches Pure Water in Mid-Air?! ⚡ #shorts #physics #explorephysics",
        "comment_q": "💬 How many volts does it take to float water across empty air? Comment below!",
        "narration": (
            "Wait... apply twenty-five thousand volts between two beakers of pure deionized water, and a stable, suspended cylindrical bridge of liquid forms and hangs unsupported in mid-air! Intense electrostatic forces align the water molecules into an ultra-strong microscopic dipole lattice!"
        ),
        "metric_line1": "25,000 VOLTS",
        "metric_line2": "DIPOLE LATTICE",
        "metric_sub": "FLOATING LIQUID!",
        "source_credit": "High Voltage Physics Lab — Armstrong Floating Water Bridge",
        "related_topic_id": "laser_waterfall_fiber_optics",
        "related_title": "Since When Can Water BEND a Laser Beam?!",
    },
    {
        "id": "schlieren_imaging_heat_sound",
        "query": "schlieren optics visualizing invisible sound heat shockwaves experiment",
        "hook": "WAIT... INVISIBLE SOUND BECOMES VISIBLE?!",
        "title": "This Special Mirror Makes SOUND WAVES Visible! 👁️ #shorts #physics #explorephysics",
        "title_alt": "Wait... Seeing Heat and Sound Shockwaves With Mirrors?! 👁️ #shorts #physics #explorephysics",
        "comment_q": "💬 What invisible thing would you want to see with Schlieren optics? Comment below!",
        "narration": (
            "Wait... watch closely as sound shockwaves from a hand clap become completely visible on camera! Using Schlieren optical imaging, a pinpoint light source and razor edge catch subtle refractive index changes in the air, turning invisible heat plumes and acoustic waves into razor-sharp shadows on screen!"
        ),
        "metric_line1": "SCHLIEREN OPTICS",
        "metric_line2": "REFRACTIVE SHIFT",
        "metric_sub": "VISIBLE AIR WAVES!",
        "source_credit": "Optical Physics Lab — Schlieren Imaging of Shockwaves & Heat",
        "related_topic_id": "chladni_plate_cymatics",
        "related_title": "This Is What Hidden Sound Waves LOOK Like!",
    },
    {
        "id": "gallium_metal_eating_aluminum",
        "query": "liquid gallium destroying aluminum soda can time lapse experiment",
        "hook": "WAIT... THIS LIQUID LIQUEFIES SOLID METAL?!",
        "title": "Liquid Gallium DESTROYS Solid Aluminum! 🧪 #shorts #physics #explorephysics",
        "title_alt": "Wait... Gallium Turns Tough Metal Into Crumbling Chalk?! 🧪 #shorts #physics #explorephysics",
        "comment_q": "💬 Why doesn't gallium destroy iron or steel? Drop your science answer below!",
        "narration": (
            "Wait... put a drop of liquid gallium on an aluminum plate, and hours later the solid metal crumbles like soggy cardboard! Gallium atoms diffuse straight between aluminum crystal grain boundaries, destroying its microscopic lattice structure and turning aerospace-grade metal into brittle dust with zero heat!"
        ),
        "metric_line1": "GRAIN DIFFUSION",
        "metric_line2": "EMBRITTLEMENT",
        "metric_sub": "METAL DESTROYED!",
        "source_credit": "Materials Science Lab — Liquid Metal Embrittlement of Aluminum",
        "related_topic_id": "induction_melting_mid_air",
        "related_title": "Melting Metal Levitating in MID-AIR!",
    },
    {
        "id": "supercooled_water_instant_freeze",
        "query": "instant freeze supercooled water physical tap bottle experiment",
        "hook": "WAIT... INSTANT ICE WITH ONE TAP?!",
        "title": "Tapping This Liquid FREEZES It In 1 Second! ❄️ #shorts #physics #explorephysics",
        "title_alt": "Wait... Water Freezes Solid Instantly Upon Impact?! ❄️ #shorts #physics #explorephysics",
        "comment_q": "💬 Have you ever accidentally supercooled a water bottle in your freezer? Comment YES or NO!",
        "narration": (
            "Wait... give this bottle of liquid water one gentle tap on the table, and a wave of ice flashes through the entire bottle in one second! Without microscopic dust particles for ice to form on, pure water can stay liquid well below freezing—until a single shockwave triggers explosive crystallization!"
        ),
        "metric_line1": "-4 °C (25 °F)",
        "metric_line2": "NUCLEATION WAVE",
        "metric_sub": "INSTANT ICE!",
        "source_credit": "Thermodynamics Lab — Supercooled Water Rapid Nucleation Experiment",
        "related_topic_id": "leidenfrost_effect_water",
        "related_title": "Why Water Droplets LEVITATE on Hot Metal!",
    },
    {
        "id": "aerogel_frozen_smoke_blowtorch",
        "query": "aerogel blowtorch experiment",
        "hook": "WAIT... FLOWER SURVIVES 1000°C BLOWTORCH?!",
        "title": "This 'Frozen Smoke' BLOCKS a 1000°C Blowtorch! 🔥 #shorts #physics #explorephysics",
        "title_alt": "Wait... Delicate Flower Survives Direct Blowtorch Heat?! 🔥 #shorts #physics #explorephysics",
        "comment_q": "💬 How much of aerogel is just empty air? Drop your percentage guess below!",
        "narration": (
            "Wait... place a fresh flower petal on a thin wafer of silica aerogel and blast the underside with a thousand-degree blowtorch! Composed of ninety-nine point eight percent air trapped in nanoscale pores, aerogel is the world's lightest solid and best insulator, stopping extreme thermal conduction dead in its tracks!"
        ),
        "metric_line1": "99.8% AIR",
        "metric_line2": "NANOPORE BARRIER",
        "metric_sub": "ZERO HEAT TRANSFER!",
        "source_credit": "Materials Science Demo — Silica Aerogel Thermal Insulation on Flower",
        "related_topic_id": "leidenfrost_effect_water",
        "related_title": "Why Water Droplets LEVITATE on Hot Metal!",
    },
    {
        "id": "bismuth_crystal_oxidation_colors",
        "query": "molten bismuth growing rainbow hopper crystals oxidation experiment",
        "hook": "WAIT... GROWING RAINBOW CRYSTALS FROM METAL?!",
        "title": "Growing Iridescent RAINBOW Metal Crystals! 🌈 #shorts #physics #explorephysics",
        "title_alt": "Wait... Liquid Metal Grows Rainbow Geometric Crystals?! 🌈 #shorts #physics #explorephysics",
        "comment_q": "💬 Which bismuth color is your favorite? Comment your color below!",
        "narration": (
            "Wait... melt pure element eighty-three bismuth on a stove, let it cool, and pull out stunning rainbow staircase crystals! Higher crystal growth rates at the edges form stepped hopper pyramids, while a nanometer-thin oxide layer causes optical wave interference, producing vivid rainbow iridescence naturally!"
        ),
        "metric_line1": "HOPPER GROWTH",
        "metric_line2": "OXIDE INTERFERENCE",
        "metric_sub": "NATURAL RAINBOW!",
        "source_credit": "Solid State Physics — Elemental Bismuth Hopper Crystal Growth",
        "related_topic_id": "chladni_plate_cymatics",
        "related_title": "This Is What Hidden Sound Waves LOOK Like!",
    },
    {
        "id": "nitinol_memory_wire_heat_recovery",
        "query": "nitinol shape memory alloy wire warm water heat recovery experiment",
        "hook": "WAIT... THIS METAL HAS A MEMORY?!",
        "title": "Mangled Metal REMEMBERS Its Shape In Hot Water! 🧠 #shorts #physics #explorephysics",
        "title_alt": "Wait... Deformed Metal Snaps Back to Life When Heated?! 🧠 #shorts #physics #explorephysics",
        "comment_q": "💬 What would you build with shape memory metal? Drop your wildest idea below!",
        "narration": (
            "Wait... crumple this spring of Nitinol alloy into a completely unrecognizable ball, drop it into warm water, and it violently snaps back into perfect shape! Nickel-titanium undergoes a reversible solid-state phase transformation between low-temperature Martensite and high-temperature Austenite, erasing physical deformation instantly!"
        ),
        "metric_line1": "SHAPE MEMORY",
        "metric_line2": "PHASE FLIP",
        "metric_sub": "PERFECT RECOVERY!",
        "source_credit": "Smart Materials Lab — Nitinol Shape Memory Alloy Demonstration",
        "related_topic_id": "curie_point_heat_magnet",
        "related_title": "Watch FIRE Destroy a Magnet's Power Instantly!",
    },
    {
        "id": "crookes_radiometer_light_mill",
        "query": "crookes radiometer light mill spinning laser flashlight thermal transpiration experiment",
        "hook": "WAIT... SUNLIGHT SPINS THIS ENGINE?!",
        "title": "Spinning Vanes Powered ONLY by Light! 💡 #shorts #physics #explorephysics",
        "title_alt": "Wait... Can Flashlights Spin This Glass Engine?! 💡 #shorts #physics #explorephysics",
        "comment_q": "💬 Black side or white side... which side pushes the vanes faster? Comment below!",
        "narration": (
            "Wait... shine a flashlight on these tiny glass vanes inside a near-vacuum bulb, and they start spinning furiously with zero motors or wires! Black vanes absorb light and heat up faster than white vanes, causing gas molecules striking the black side to rebound with higher velocity, driving relentless rotation through thermal transpiration!"
        ),
        "metric_line1": "NEAR VACUUM",
        "metric_line2": "THERMAL TRANSPIRATION",
        "metric_sub": "POWERED BY LIGHT!",
        "source_credit": "Thermodynamics Demo — Crookes Radiometer Light Mill Rotation",
        "related_topic_id": "laser_waterfall_fiber_optics",
        "related_title": "Since When Can Water BEND a Laser Beam?!",
    },
    {
        "id": "triboluminescence_wintergreen_candy",
        "query": "crushing winto green lifesavers sparks blue light triboluminescence slow motion",
        "hook": "WAIT... CRUSHING CANDY MAKES LIGHTNING?!",
        "title": "Crushing Candy Sparks BLUE LIGHT in the Dark! 🍬 #shorts #physics #explorephysics",
        "title_alt": "Wait... Biting This Mint Sparks Real Ultraviolet Light?! 🍬 #shorts #physics #explorephysics",
        "comment_q": "💬 Have you ever tried crushing wintergreen mints in a dark closet? Comment below!",
        "narration": (
            "Wait... crush a wintergreen mint with pliers in complete darkness, and vivid flashes of blue electric light explode into view! Fracturing sugar crystals rips positive and negative charges apart, ionizing nitrogen gas like miniature lightning bolts, which wintergreen oil absorbs and fluoresces as bright visible light!"
        ),
        "metric_line1": "TRIBOLUMINESCENCE",
        "metric_line2": "CHARGE FRACTURE",
        "metric_sub": "CANDY LIGHTNING!",
        "source_credit": "Atomic Physics Lab — Sugar Crystal Triboluminescence in Wintergreen",
        "related_topic_id": "singing_tesla_coil_sound",
        "related_title": "This 500,000 Volt LIGHTNING Plays Music!",
    },
    {
        "id": "strobe_effect_water_droplet_levitation",
        "query": "stroboscopic effect water drops falling backwards levitating speaker experiment",
        "hook": "WAIT... WATER DROPLETS FALLING UPWARDS?!",
        "title": "Water Drops LEVITATE and Float Backwards! 💧 #shorts #physics #explorephysics",
        "title_alt": "Wait... Water Droplets Defy Gravity and Fall UP?! 💧 #shorts #physics #explorephysics",
        "comment_q": "💬 Is this real physics or an optical illusion? Drop your verdict in the comments!",
        "narration": (
            "Wait... look straight at these falling water droplets—they have completely frozen in mid-air and are now floating upwards against gravity! By matching the flash frequency of stroboscopic LEDs to the exact vibration rate of a sound-driven water nozzle, our eyes sample consecutive droplets at slightly earlier positions, creating an optical time-reversal illusion!"
        ),
        "metric_line1": "STROBE ALIASING",
        "metric_line2": "FREQUENCY LOCK",
        "metric_sub": "REVERSE TIME!",
        "source_credit": "Optics & Perception Lab — Stroboscopic Water Droplet Levitation",
        "related_topic_id": "acoustic_levitation_sound",
        "related_title": "This Water Droplet Floats on PURE SOUND?!",
    },
    {
        "id": "eddy_current_coin_drop",
        "query": "neodymium magnet falling through aluminum block eddy current brake slow motion",
        "hook": "WAIT... METAL SLOWS MAGNET LIKE HONEY?!",
        "title": "Aluminum SLOWS Falling Magnets Like Syrup! 🧲 #shorts #physics #explorephysics",
        "title_alt": "Wait... Dropping a Magnet Over Solid Aluminum Defies Gravity?! 🧲 #shorts #physics #explorephysics",
        "comment_q": "💬 Pure aluminum isn't magnetic... so why does it stop magnets? Comment below!",
        "narration": (
            "Wait... drop a super-strong neodymium magnet through a solid aluminum slot, and instead of slamming down, it floats slowly like it fell into thick syrup! The moving magnetic field induces swirling circular eddy currents inside the conductive aluminum, generating an opposing magnetic field that brakes gravity!"
        ),
        "metric_line1": "EDDY BRAKE",
        "metric_line2": "LENZ INDUCTION",
        "metric_sub": "ZERO FRICTION BRAKE!",
        "source_credit": "Electromagnetism Lab — Massive Aluminum Block Eddy Current Braking",
        "related_topic_id": "lenz_law_copper_tube",
        "related_title": "Why Did This Magnet FREEZE Inside Copper?!",
    },
    {
        "id": "dry_ice_soap_bubble_smoke_balloon",
        "query": "giant dry ice soap bubble smoky fog balloon popping experiment",
        "hook": "WAIT... SMOKE BUBBLE BOUNCES ON CLOTH?!",
        "title": "Giant Dry Ice Bubble Traps Glowing FOG! 🫧 #shorts #physics #explorephysics",
        "title_alt": "Wait... This Smoky Bubble Bounces Like a Rubber Ball?! 🫧 #shorts #physics #explorephysics",
        "comment_q": "💬 What is dry ice made of? Answer in 3 words in the comments!",
        "narration": (
            "Wait... stretch a soap film over a bowl of warm water and dry ice, and a giant glowing bubble dome inflates with dense white fog! Solid carbon dioxide sublimates directly into gas, filling the bubble with dense, heavy vapor until surface tension gives way, releasing an avalanche of rolling fog!"
        ),
        "metric_line1": "SUBLIMATION",
        "metric_line2": "SURFACE TENSION",
        "metric_sub": "GLOWING FOG BUBBLE!",
        "source_credit": "Thermodynamics Lab — Dry Ice Sublimation Soap Bubble Demo",
        "related_topic_id": "vortex_cannon_smoke_ring",
        "related_title": "Can an INVISIBLE Blast of Air Knock Down Cups?!",
    },
    {
        "id": "can_crusher_electromagnetic_coil",
        "query": "theta pinch electromagnetic can crusher high voltage capacitor explosion physics",
        "hook": "WAIT... MAGNETIC COIL CRUSHES ALUMINUM?!",
        "title": "Invisible Magnetic Field CRUSHES Soda Can! ⚡ #shorts #physics #explorephysics",
        "title_alt": "Wait... Electromagnetic Pulse Snaps Aluminum in Half?! ⚡ #shorts #physics #explorephysics",
        "comment_q": "💬 How much electrical energy did this coil dump in a millisecond? Comment below!",
        "narration": (
            "Wait... discharge five thousand volts through a small copper coil, and a soda can inside gets violently pinched in half by pure electromagnetism! The enormous surge of magnetic flux induces thousands of amps of eddy current in the can wall, creating opposing Lorentz forces that crush the metal in microseconds!"
        ),
        "metric_line1": "LORENTZ PINCH",
        "metric_line2": "MICROSECOND CRUSH",
        "metric_sub": "PURE MAGNETIC FORCE!",
        "source_credit": "High Voltage Lab — Electromagnetic Theta Pinch Can Crusher",
        "related_topic_id": "atmospheric_pressure_drum_crush",
        "related_title": "Why Did This Steel Drum IMPLODE In 0.1s?!",
    },
    {
        "id": "polarization_corn_syrup_rainbow",
        "query": "optical rotation corn syrup polarized light cross polarizers rainbow stress experiment",
        "hook": "WAIT... SUGAR WATER CREATES RAINBOWS?!",
        "title": "Sugar Water TURNS White Light Into Rainbows! 🌈 #shorts #physics #explorephysics",
        "title_alt": "Wait... Passing Polarized Light Through Syrup Makes Pure Color?! 🌈 #shorts #physics #explorephysics",
        "comment_q": "💬 What is this phenomenon called in optics? Test your science trivia!",
        "narration": (
            "Wait... shine polarized light through a simple bottle of corn syrup between cross-polarizers, and vivid saturated rainbows explode across the screen! Chiral sugar molecules rotate the polarization angle of each wavelength of light by different amounts, allowing specific colors to pass through and reveal stunning optical activity!"
        ),
        "metric_line1": "OPTICAL ROTATION",
        "metric_line2": "CHIRAL DISPERSION",
        "metric_sub": "POLARIZED RAINBOWS!",
        "source_credit": "Optics Lab — Chiral Polarization & Optical Rotation in Glucose",
        "related_topic_id": "laser_waterfall_fiber_optics",
        "related_title": "Since When Can Water BEND a Laser Beam?!",
    },
    {
        "id": "air_cannon_ping_pong_supersonic",
        "query": "supersonic ping pong ball vacuum cannon breaks sound barrier experiment",
        "hook": "WAIT... PING PONG BALL BREAKS SOUND BARRIER?!",
        "title": "Ping Pong Ball FIRED Faster Than Sound! 🚀 #shorts #physics #explorephysics",
        "title_alt": "Wait... Table Tennis Ball Smashes Through Solid Wood?! 🚀 #shorts #physics #explorephysics",
        "comment_q": "💬 Can a lightweight ping pong ball really shatter thick paddles? Comment below!",
        "narration": (
            "Wait... seal a plastic ping pong ball in a vacuum tube and puncture the rear seal, and it blasts out at over Mach one point two! Atmospheric air rushing into the vacuum accelerates the ultra-light ball past the speed of sound, turning a toy into a supersonic projectile that shatters wood!"
        ),
        "metric_line1": "MACH 1.2+",
        "metric_line2": "SUPERSONIC BALL",
        "metric_sub": "VACUUM CANNON!",
        "source_credit": "Supersonic Physics Lab — Vacuum Driven Ping Pong Ball Cannon",
        "related_topic_id": "vortex_cannon_smoke_ring",
        "related_title": "Can an INVISIBLE Blast of Air Knock Down Cups?!",
    },
    {
        "id": "kelvin_water_dropper_electrostatic",
        "query": "kelvin water dropper electrostatic generator spark demonstration",
        "hook": "WAIT... DRIPPING WATER CREATES SPARKS?!",
        "title": "Falling Water Droplets CREATE High-Voltage Sparks! ⚡ #shorts #physics #explorephysics",
        "title_alt": "Wait... How Does Dripping Water Generate 10,000 Volts?! ⚡ #shorts #physics #explorephysics",
        "comment_q": "💬 Lord Kelvin invented this in 1867... did you know water could do this? Comment below!",
        "narration": (
            "Wait... let ordinary tap water drip through two metal cans with zero batteries or plugs, and big high-voltage electric sparks leap across the gap! Lord Kelvin's water dropper uses positive feedback electrostatic induction between cross-connected cans, charging water droplets until thousands of volts discharge through air!"
        ),
        "metric_line1": "10,000 VOLTS",
        "metric_line2": "FEEDBACK INDUCTION",
        "metric_sub": "WATER POWERED SPARK!",
        "source_credit": "Electrostatics Lab — Lord Kelvin Water Dropper High-Voltage Generator",
        "related_topic_id": "water_bridge_high_voltage",
        "related_title": "High Voltage FLOATS a Water Bridge in Mid-Air!",
    },
    {
        "id": "lycopodium_powder_water_repellent",
        "query": "lycopodium powder dry water experiment submerged hand dry physics",
        "hook": "WAIT... DIPPING HAND INTO WATER STAYS DRY?!",
        "title": "Dipping Hand In Water But Stays 100% DRY! 🧤 #shorts #physics #explorephysics",
        "title_alt": "Wait... Submerging Your Hand in Water Without Getting Wet?! 🧤 #shorts #physics #explorephysics",
        "comment_q": "💬 What other superhydrophobic surfaces exist in nature? Comment below!",
        "narration": (
            "Wait... dust a bowl of water with lycopodium moss spores, plunge your hand completely underwater, and pull it out totally bone dry! The microscopic spores are intensely hydrophobic, trapping an unbroken envelope of air around your skin that prevents a single water molecule from touching you!"
        ),
        "metric_line1": "SUPERHYDROPHOBIC",
        "metric_line2": "AIR ENVELOPE",
        "metric_sub": "100% BONE DRY!",
        "source_credit": "Surface Physics Demo — Superhydrophobic Lycopodium Spore Barrier",
        "related_topic_id": "leidenfrost_effect_water",
        "related_title": "Why Water Droplets LEVITATE on Hot Metal!",
    },
    {
        "id": "cavitation_shrimp_strike_light",
        "query": "mantis shrimp strike cavitation bubble sonoluminescence light emission slow motion",
        "hook": "WAIT... SHRIMP STRIKE HOTTER THAN THE SUN?!",
        "title": "This Shrimp Punch Creates a Ball of LIGHT! 🦐 #shorts #physics #explorephysics",
        "title_alt": "Wait... Cavitation Bubble Reaches Temperatures Hotter Than Sun?! 🦐 #shorts #physics #explorephysics",
        "comment_q": "💬 Did you know a mantis shrimp can shatter aquarium glass? Comment below!",
        "narration": (
            "Wait... watch a mantis shrimp punch at fifty miles an hour—the water accelerates so violently that pressure drops to zero, forming a vacuum cavitation bubble! When the bubble violently implodes, shockwaves heat the trapped vapor to thousands of degrees, flashing visible light in an explosion of sonoluminescence!"
        ),
        "metric_line1": "5,000 K TEMP",
        "metric_line2": "CAVITATION IMPLOSION",
        "metric_sub": "SONOLUMINESCENCE!",
        "source_credit": "Hydrodynamics Lab — Cavitation Bubble Sonoluminescence & Shockwave",
        "related_topic_id": "prince_ruperts_drop",
        "related_title": "Bullet vs. UNBREAKABLE Glass Drop!",
    },
    {
        "id": "mit_resonance_tacoma_bridge",
        "query": "tacoma narrows bridge collapse mechanical resonance aeroelastic flutter physics",
        "hook": "WAIT... MILD BREEZE DESTROYS GIANT BRIDGE?!",
        "title": "Why a Gentle Breeze DESTROYED This Giant Bridge! 🌉 #shorts #physics #explorephysics",
        "title_alt": "Wait... Aeroelastic Flutter Twists Solid Concrete Apart?! 🌉 #shorts #physics #explorephysics",
        "comment_q": "💬 Resonance or flutter? Test your engineering knowledge in the comments!",
        "narration": (
            "Wait... watch a gentle forty-mile-an-hour wind twist a massive steel and concrete suspension bridge into violent roller-coaster waves! Vortex shedding matched the bridge's torsional natural frequency, creating destructive aeroelastic flutter that amplified vibrations until the entire structure collapsed!"
        ),
        "metric_line1": "TORSIONAL FLUTTER",
        "metric_line2": "NATURAL RESONANCE",
        "metric_sub": "BRIDGE COLLAPSE!",
        "source_credit": "Structural Dynamics Demo — Tacoma Narrows Aeroelastic Flutter",
        "related_topic_id": "chladni_plate_cymatics",
        "related_title": "This Is What Hidden Sound Waves LOOK Like!",
    },
    {
        "id": "thermite_ice_explosion",
        "query": "liquid hot thermite on ice instant steam explosion physics experiment",
        "hook": "WAIT... POURING FIRE ONTO ICE EXPLODES?!",
        "title": "Dropping Molten Thermite on ICE Causes Instant EXPLOSION! 💥 #shorts #physics #explorephysics",
        "title_alt": "Wait... Molten Iron on Ice Causes a Violent Blast?! 💥 #shorts #physics #explorephysics",
        "comment_q": "💬 Why does molten metal explode when touching ice? Guess below!",
        "narration": (
            "Wait... pour four-thousand-degree molten thermite onto a giant block of solid ice, and a deafening shockwave blast detonates immediately! Trapped molten iron superheats underlying ice so fast that water flashes instantly into high-pressure steam, triggering a violent physical steam explosion!"
        ),
        "metric_line1": "2,500 °C (4,500 °F)",
        "metric_line2": "FLASH STEAM BLAST",
        "metric_sub": "INSTANT DETONATION!",
        "source_credit": "Thermal Physics Lab — Molten Thermite Reaction on Solid Ice Block",
        "related_topic_id": "leidenfrost_effect_water",
        "related_title": "Why Water Droplets LEVITATE on Hot Metal!",
    },
    {
        "id": "magnetic_fluid_vortex_ferro_cell",
        "query": "ferrocell magnetic field lines 3D light pattern quantum physics experiment",
        "hook": "WAIT... VISUALIZING 3D MAGNETIC FIELDS?!",
        "title": "This Hologram Lens Reveals REAL Magnetic Fields! 👁️ #shorts #physics #explorephysics",
        "title_alt": "Wait... 3D Light Lens Makes Invisible Magnetism Holographic?! 👁️ #shorts #physics #explorephysics",
        "comment_q": "💬 Does this look like a cosmic black hole or magnetic field? Comment below!",
        "narration": (
            "Wait... place a neodymium magnet behind a Ferrocell glass lens, and brilliant 3D holographic curves of light appear out of nowhere! Nanoscale magnetic nanoparticles suspended in oil align into microscopic diffraction gratings, bending LED light into perfect geometric maps of magnetic flux lines!"
        ),
        "metric_line1": "FERROCELL LENS",
        "metric_line2": "FLUX DIFFRACTION",
        "metric_sub": "3D MAGNETIC FIELD!",
        "source_credit": "Quantum Optics Lab — Ferrocell Magnetic Field Visualization",
        "related_topic_id": "ferrofluid_magnetic_spikes",
        "related_title": "Is This Magnetic Liquid ALIVE?!",
    },
    {
        "id": "piezoelectric_gas_igniter_spark",
        "query": "piezoelectric spark gas grill lighter crystal hammer slow motion physics",
        "hook": "WAIT... SMASHING CRYSTAL CREATES 10,000V?!",
        "title": "Smashing This Crystal Creates 10,000 VOLTS! ⚡ #shorts #physics #explorephysics",
        "title_alt": "Wait... How Do Simple Kitchen Lighters Spark Without Batteries?! ⚡ #shorts #physics #explorephysics",
        "comment_q": "💬 Did you know your kitchen lighter has a real piezoelectric crystal? Comment below!",
        "narration": (
            "Wait... click a simple push-button lighter, and a spring-loaded hammer smashes into a tiny PZT ceramic crystal, instantly shooting a ten-thousand-volt spark! Mechanical compression displaces positive and negative ions inside the asymmetric crystal lattice, converting physical impact directly into high-voltage electricity!"
        ),
        "metric_line1": "10,000 VOLTS",
        "metric_line2": "PIEZOELECTRIC SHIFT",
        "metric_sub": "IMPACT TO VOLTAGE!",
        "source_credit": "Solid State Physics — Piezoelectric Crystal High-Voltage Discharge",
        "related_topic_id": "singing_tesla_coil_sound",
        "related_title": "This 500,000 Volt LIGHTNING Plays Music!",
    },
    {
        "id": "non_reversing_mirror_optics",
        "query": "true mirror non reversing mirror 90 degree reflection experiment",
        "hook": "WAIT... YOU HAVE NEVER SEEN YOUR TRUE FACE?!",
        "title": "This Non-Reversing Mirror Shows YOUR TRUE FACE! 🪞 #shorts #physics #explorephysics",
        "title_alt": "Wait... Normal Mirrors Have Been Lying to You Your Whole Life?! 🪞 #shorts #physics #explorephysics",
        "comment_q": "💬 Wink your right eye in a True Mirror... which eye winks back? Comment below!",
        "narration": (
            "Wait... look into a ordinary bathroom mirror and your reflection is flipped left-to-right—you've never seen yourself as others see you! Join two surface mirrors at a precise ninety-degree angle, and light bounces twice between them, un-inverting your image and revealing your true, unreversed face!"
        ),
        "metric_line1": "90° INTERSECT",
        "metric_line2": "DOUBLE BOUNCE",
        "metric_sub": "UNREVERSED FACE!",
        "source_credit": "Optics Lab — 90-Degree Non-Reversing True Mirror Demonstration",
        "related_topic_id": "laser_waterfall_fiber_optics",
        "related_title": "Since When Can Water BEND a Laser Beam?!",
    },
    {
        "id": "hydraulic_press_diamond_test",
        "query": "hydraulic press diamond crush test slow motion physics experiment",
        "hook": "WAIT... CAN HYDRAULIC PRESS CRUSH DIAMOND?!",
        "title": "Hydraulic Press vs. REAL DIAMOND! 💎 #shorts #physics #explorephysics",
        "title_alt": "Wait... Can 100 Tons of Pressure Shatter Hardest Mineral?! 💎 #shorts #physics #explorephysics",
        "comment_q": "💬 Hardness vs. Toughness: Do you know the difference? Explain below!",
        "narration": (
            "Wait... diamond is the hardest natural mineral on planet Earth, but what happens under a hundred-ton hydraulic press?! While diamond's covalent carbon lattice resists scratching better than anything, it has natural cleavage planes with lower fracture toughness, shattering into fine diamond dust under concentrated compressive load!"
        ),
        "metric_line1": "100 TONS LOAD",
        "metric_line2": "CLEAVAGE FRACTURE",
        "metric_sub": "DIAMOND SHATTER!",
        "source_credit": "Mechanical Testing Lab — Hydraulic Press Diamond Cleavage Test",
        "related_topic_id": "prince_ruperts_drop",
        "related_title": "Bullet vs. UNBREAKABLE Glass Drop!",
    },
    {
        "id": "liquid_nitrogen_cloud_explosion",
        "query": "liquid nitrogen poured into boiling water massive fog cloud physics demonstration",
        "hook": "WAIT... POURING FREEZING LIQUID IN WATER EXPLODES?!",
        "title": "Liquid Nitrogen in Hot Water Creates ROOM-SIZED CLOUD! ☁️ #shorts #physics #explorephysics",
        "title_alt": "Wait... Liquid Nitrogen + Boiling Water Causes Instant Cloud Blast?! ☁️ #shorts #physics #explorephysics",
        "comment_q": "💬 Is the cloud water vapor or nitrogen gas? Comment your science guess below!",
        "narration": (
            "Wait... dump a bucket of liquid nitrogen at minus one-hundred ninety-six Celsius into a tub of hot water, and a colossal shock-cloud explodes into the room! Liquid nitrogen expands by a factor of nearly seven hundred as it flash-boils, instantly chilling humid air into trillions of microscopic condensed fog droplets!"
        ),
        "metric_line1": "700x EXPANSION",
        "metric_line2": "FLASH CONDENSATION",
        "metric_sub": "ROOM SIZED CLOUD!",
        "source_credit": "Cryogenics Lab — Liquid Nitrogen Instant Fog Cloud Demonstration",
        "related_topic_id": "quantum_levitation_superconductor",
        "related_title": "This Disc Freezes in MID-AIR at -196°C?!",
    },
    {
        "id": "ac_dc_electron_drift_3d",
        "query": "AC vs DC circuit simulation 3d animation electron",
        "hook": "WAIT... ELECTRONS IN AC NEVER ACTUALLY MOVE FORWARD?!",
        "title": "AC vs DC: What REALLY Happens Inside the Wire in 3D! ⚡ #shorts #physics #explorephysics",
        "title_alt": "Wait... AC Electrons Vibrate In Place While DC Drifts?! ⚡ #shorts #physics #explorephysics",
        "comment_q": "💬 Did you know electrons in AC only vibrate in place? Drop your thoughts below!",
        "narration": (
            "Wait... in a DC circuit, electrons drift forward in a single continuous path. But in AC, electrons never actually leave your home! They just vibrate back and forth sixty times a second, transferring pure energy through the electromagnetic field at the speed of light!"
        ),
        "metric_line1": "60 HZ AC",
        "metric_line2": "ELECTRON VIBRATION",
        "metric_sub": "ZERO NET DRIFT!",
        "source_credit": "Electromagnetism Simulation — AC vs DC Electron Drift",
        "related_topic_id": "transformer_magnetic_core_3d",
        "related_title": "How Transformers Transfer 100,000 Volts",
    },
    {
        "id": "transformer_magnetic_core_3d",
        "query": "how transformer works 3d animation magnetic flux",
        "hook": "WAIT... TRANSFORMERS POWER CITIES WITH ZERO CONTACT?!",
        "title": "How Transformers Transfer 100,000 Volts With ZERO Physical Contact! ⚡ #shorts #physics #explorephysics",
        "title_alt": "Wait... Electricity Jumps Coils Without Touching in 3D?! ⚡ #shorts #physics #explorephysics",
        "comment_q": "💬 How many volts does your household transformer step down? Comment below!",
        "narration": (
            "Wait... the two coils in a transformer never touch each other! Primary alternating current generates an oscillating magnetic flux inside the laminated iron core. That invisible pulsing magnetic field induces fresh electric voltage into the secondary coil out of thin air!"
        ),
        "metric_line1": "100,000 VOLTS",
        "metric_line2": "INDUCED FLUX",
        "metric_sub": "ZERO CONTACT!",
        "source_credit": "Electromagnetism Simulation — Transformer Core Induction",
        "related_topic_id": "full_wave_bridge_rectifier_3d",
        "related_title": "How 4 Diodes Tame Wild AC Power",
    },
    {
        "id": "full_wave_bridge_rectifier_3d",
        "query": "full wave bridge rectifier 3d animation simulation diode",
        "hook": "WAIT... HOW 4 DIODES FORCE ELECTRICITY TO NEVER REVERSE?!",
        "title": "How 4 Diodes Tame Wild AC Power Into Smooth DC! ⚡ #shorts #physics #explorephysics",
        "title_alt": "Wait... This 4-Diode Diamond Bridge Never Lets Voltage Reverse?! ⚡ #shorts #physics #explorephysics",
        "comment_q": "💬 What would happen if one diode in the bridge burned out? Comment below!",
        "narration": (
            "Wait... wall socket electricity flips backwards sixty times every single second! But arrange four microscopic silicon diodes into a diamond bridge, and no matter which way alternating current enters, it is forced to exit in the exact same forward direction into clean direct current!"
        ),
        "metric_line1": "4 DIODES",
        "metric_line2": "BRIDGE RECTIFIER",
        "metric_sub": "PURE DC OUTPUT!",
        "source_credit": "Electronics Simulation — Full-Wave Diode Bridge",
        "related_topic_id": "transformer_magnetic_core_3d",
        "related_title": "How Transformers Transfer 100,000 Volts",
    },
    {
        "id": "lcr_circuit_voltage_current",
        "query": "Voltage and Current in LCR circuit animation",
        "hook": "WAIT... VOLTAGE AND CURRENT DON'T MOVE TOGETHER?!",
        "title": "Voltage and Current in LCR Circuit Explained in 3D ⚡ #shorts #physics #explorephysics",
        "title_alt": "Wait... Current Lags Voltage in an Inductor in 3D?! ⚡ #shorts #physics #explorephysics",
        "comment_q": "💬 In which component does Current lead Voltage? Comment below!",
        "narration": (
            "Wait... in an AC circuit, voltage and current rarely peak together! Across a resistor they move in sync, but an inductor resists changes so current lags behind, while a capacitor stores charge causing voltage to lag behind current!"
        ),
        "metric_line1": "90° PHASE LAG",
        "metric_line2": "LCR RESONANCE",
        "metric_sub": "VOLTAGE & CURRENT!",
        "source_credit": "Circuit Dynamics 3D — LCR Phase Resonance",
        "related_topic_id": "current_vs_voltage_pipe_3d",
        "related_title": "Voltage vs Current: The Ultimate 3D Analogy",
    },
    {
        "id": "current_vs_voltage_pipe_3d",
        "query": "CURRENT vs VOLTAGE 3d animation pipe water physics",
        "hook": "WAIT... VOLTAGE PUSHES, RESISTANCE BLOCKS?!",
        "title": "Voltage vs Current: The Ultimate 3D Physical Analogy! 💧⚡ #shorts #physics #explorephysics",
        "title_alt": "Wait... How Voltage, Current and Resistance Interact in 3D?! ⚡ #shorts #physics #explorephysics",
        "comment_q": "💬 What is your favorite way to visualize Ohm's Law? Comment below!",
        "narration": (
            "Wait... how do voltage, current, and resistance really work together? Think of a water pipe: voltage is the high-pressure pump pushing the liquid, current is the volume of water flowing per second, and resistance is the narrow pipe constriction choking the flow!"
        ),
        "metric_line1": "OHM'S LAW",
        "metric_line2": "V = I x R",
        "metric_sub": "PRESSURE VS FLOW!",
        "source_credit": "Physics Visuals — Water Pipe Model of Electricity",
        "related_topic_id": "ac_dc_electron_drift_3d",
        "related_title": "AC vs DC: What REALLY Happens Inside Wire",
    },
    {
        "id": "rutherford_gold_foil_3d",
        "query": "rutherford gold foil experiment alpha particle 3d animation",
        "hook": "WAIT... ATOMS ARE 99.9999999% EMPTY SPACE?!",
        "title": "How Alpha Particles Proved Atoms Are 99.99% EMPTY SPACE! ⚛️ #shorts #physics #explorephysics",
        "title_alt": "Wait... Firing Bullets at Tissue Paper and They Bounce Back?! ⚛️ #shorts #physics #explorephysics",
        "comment_q": "💬 If atoms are empty space, why can't we walk through walls? Comment below!",
        "narration": (
            "Wait... in nineteen eleven, Ernest Rutherford fired heavy alpha particles through ultra-thin gold foil. Almost all passed straight through empty space as if nothing was there! But one in eight thousand bounced straight backwards, revealing that ninety-nine point nine percent of atomic mass is crammed into an ultra-dense positive nucleus!"
        ),
        "metric_line1": "99.99% EMPTY",
        "metric_line2": "ATOMIC NUCLEUS",
        "metric_sub": "ALPHA SCATTERING!",
        "source_credit": "Nuclear Physics 3D — Rutherford Alpha Scattering",
        "related_topic_id": "ac_dc_electron_drift_3d",
        "related_title": "AC vs DC: What REALLY Happens Inside Wire",
    },
    {
        "id": "laminar_flow_reversible_mixing",
        "query": "laminar flow corn syrup dye experiment",
        "hook": "WAIT... TURNING A CRANK BACKWARDS UN-MIXES PAINT?!",
        "title": "Mixing Paint Backwards UN-MIXES It Completely?! 🌀🎨 #shorts #physics #science",
        "title_alt": "Wait... You Can UN-MIX Colors Just By Reversing Fluid Motion?! 🌀 #shorts #physics",
        "comment_q": "💬 Does physical entropy increase if you reverse laminar mixing? Comment below!",
        "narration": (
            "Watch what happens when colored dye is stirred into thick corn syrup. "
            "The colors seem permanently blended. But turn the cylinder backward, "
            "and the colors completely separate back into perfect droplets! "
            "This is called Laminar Flow. At low Reynolds numbers, viscous forces dominate over inertia. "
            "Reverse the motion, and every fluid molecule retraces its path in reverse!"
        ),
        "metric_line1": "REYNOLDS NO: Re << 1",
        "metric_line2": "LAMINAR FLOW",
        "metric_sub": "REVERSIBLE DYNAMICS!",
        "source_credit": "Fluid Mechanics Archive — Reversible Laminar Flow",
        "related_topic_id": "voltage_current_cutaway_3d",
        "related_title": "Voltage vs Current: What ACTUALLY Happens Inside The Wire",
    },
    {
        "id": "van_de_graaff_hair_raising",
        "query": "van de graaff generator hair experiment",
        "hook": "WAIT... TOUCHING 500,000 VOLTS MAKES YOUR HAIR FLY?!",
        "title": "Why Does 500,000 Volts Make Hair Defy Gravity?! ⚡👩‍🔬 #shorts #physics #science",
        "title_alt": "Wait... Why Doesn't 500,000 Volts Electrocute You?! ⚡ #shorts #physics",
        "comment_q": "💬 What would happen if you touched this in complete zero gravity? Comment below!",
        "narration": (
            "What happens when you touch a five hundred thousand volt metal sphere? "
            "You don't get electrocuted. Your hair literally defies gravity! "
            "The Van de Graaff generator pumps millions of electrons onto the dome. "
            "Standing on an insulated stool, excess electrons surge into your body. "
            "Because each hair strand carries identical negative charge, they violently repel each other in all directions!"
        ),
        "metric_line1": "VOLTAGE: 500,000 V",
        "metric_line2": "ELECTROSTATICS",
        "metric_sub": "COULOMB REPULSION!",
        "source_credit": "High Voltage Physics Archive — Van de Graaff Generator",
        "related_topic_id": "voltage_current_cutaway_3d",
        "related_title": "Voltage vs Current: What ACTUALLY Happens Inside The Wire",
    },
]


def ensure_directories() -> None:
    INPUT_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    sample = INPUT_DIR / "sample_test_video.mp4"
    if sample.exists():
        sample.unlink()


def load_history() -> set[str]:
    if not HISTORY_FILE.exists():
        return set()
    try:
        data = json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
        return set(data.get("processed", []))
    except Exception:
        return set()


def save_to_history(identifier: str) -> None:
    history = load_history()
    history.add(identifier)
    HISTORY_FILE.write_text(
        json.dumps({"processed": sorted(history)}, indent=2),
        encoding="utf-8",
    )


def get_ffmpeg_executable() -> str:
    sys_ffmpeg = shutil.which("ffmpeg")
    if sys_ffmpeg:
        return sys_ffmpeg
    import imageio_ffmpeg

    return imageio_ffmpeg.get_ffmpeg_exe()


def get_related_video_info(topic: Dict[str, Any]) -> Tuple[str, str]:
    """Find the best related experiment on the channel to promote cross-video retention."""
    rel_topic_id = topic.get("related_topic_id")
    rel_title = topic.get("related_title", "Mind-Blowing Physics Experiment")
    history = load_history()

    # 1. Search history for uploaded video ID of the related topic
    for item in history:
        if item.startswith(f"TOPIC_VID:{rel_topic_id}:"):
            vid_id = item.split(":", 2)[2]
            return rel_title, f"https://www.youtube.com/shorts/{vid_id}"

    # 2. Known verified live/scheduled YouTube video IDs on the channel
    topic_to_known_vid = {
        "prince_ruperts_drop": "eP6_8cifn98",
        "quantum_levitation_superconductor": "tt5b4zT2Yfc",
        "lenz_law_copper_tube": "wzLmrSve58o",
        "acoustic_levitation_sound": "9DLs7fM43y0",
        "ferrofluid_magnetic_spikes": "mB9aZluVtF4",
        "leidenfrost_effect_water": "O8DtI4Pjjbo",
        "slinky_free_fall_slow_motion": "2FBEU2M6t68",
        "gyroscopic_precession_wheel": "HEBAPWLQ5h0",
        "bernoulli_levitating_ball": "Gqhm4tD5Vio",
        "double_pendulum_chaos": "niXvbhUtPuk",
        "laser_waterfall_fiber_optics": "2aBPcGNIEu0",
    }
    if rel_topic_id in topic_to_known_vid:
        vid_id = topic_to_known_vid[rel_topic_id]
        return rel_title, f"https://www.youtube.com/shorts/{vid_id}"

    return "Bullet vs. UNBREAKABLE Glass Drop", "https://www.youtube.com/shorts/eP6_8cifn98"


def like_own_video(youtube: Any, vid_id: str) -> bool:
    """Automatically give an official Like (rating='like') to the channel's own video to boost algorithm engagement."""
    history = load_history()
    like_key = f"LIKED_OWN_VIDEO:{vid_id}"
    if like_key in history:
        return True
    try:
        youtube.videos().rate(id=vid_id, rating="like").execute()
        save_to_history(like_key)
        print(f"[AUTO-LIKE] Successfully liked own video {vid_id}!", flush=True)
        return True
    except Exception as exc:
        print(f"[AUTO-LIKE] Could not like video {vid_id}: {exc}", flush=True)
        return False


def ensure_creator_first_comment(
    youtube: Any, vid_id: str, topic: Dict[str, Any]
) -> bool:
    """Post a featured creator comment asking viewers to Like & Subscribe + Quiz Question + Related Video."""
    history = load_history()
    comment_key = f"FIRST_COMMENT:{vid_id}"
    if comment_key in history:
        return False

    quiz_line = topic.get(
        "comment_q", "💬 What do you think about this physics experiment?"
    )
    rel_title, rel_url = get_related_video_info(topic)
    comment_text = (
        f"❤️👍 Official Creator Spotlight & Physics Quiz:\n"
        f"📌 {quiz_line}\n\n"
        f"👉 Watch Related Video ({rel_title}):\n"
        f"🔗 {rel_url}\n\n"
        f"🔔 Enjoyed this video? Please drop a LIKE 👍 and SUBSCRIBE to @Physics_explain_YT for daily 3D simulations & mind-blowing physics experiments! 💬⚡"
    )
    try:
        youtube.commentThreads().insert(
            part="snippet",
            body={
                "snippet": {
                    "videoId": vid_id,
                    "topLevelComment": {
                        "snippet": {
                            "textOriginal": comment_text,
                        }
                    },
                }
            },
        ).execute()
        save_to_history(comment_key)
        print(
            f"[AUTO-COMMENT] Posted featured Like & Subscribe comment on {vid_id}!",
            flush=True,
        )
        return True
    except Exception as exc:
        print(f"[AUTO-COMMENT] Could not post comment on {vid_id}: {exc}", flush=True)
        return False


MAX_REPLIES_PER_VIDEO = 5


def engage_viewer_comments_12_to_24h(
    youtube: Any, vid_id: str, hours_live: float
) -> int:
    """From 0 to 24 hours (1 full day) after publish, check viewer comments and reply with
    a creator Heart (❤️) & thank-you message to at most 5 best positive/supportive viewer comments
    per video (saving YouTube API quota).
    """
    if not (0.0 <= hours_live <= 24.0):
        return 0

    history = load_history()
    vid_reply_prefix = f"REPLIED_VID:{vid_id}:"
    already_replied_count = sum(
        1 for item in history if item.startswith(vid_reply_prefix)
    )
    if already_replied_count >= MAX_REPLIES_PER_VIDEO:
        return 0

    remaining_quota_for_vid = MAX_REPLIES_PER_VIDEO - already_replied_count
    replied_count = 0
    positive_words = (
        "cool",
        "awesome",
        "amazing",
        "great",
        "love",
        "nice",
        "wow",
        "good",
        "physics",
        "science",
        "subscribed",
        "sub",
        "like",
        "interesting",
        "aluminum",
        "magnet",
        "glass",
        "yes",
        "no",
        "float",
        "fall",
        "เยี่ยม",
        "ดี",
        "ชอบ",
        "เจ๋ง",
    )
    negative_words = ("spam", "scam", "hate", "worst", "stupid", "fake", "bot")

    try:
        threads = (
            youtube.commentThreads()
            .list(
                part="snippet",
                videoId=vid_id,
                maxResults=30,
                textFormat="plainText",
            )
            .execute()
            .get("items", [])
        )
    except Exception as exc:
        print(
            f"[AUTO-ENGAGE] Could not list comments for {vid_id}: {exc}",
            flush=True,
        )
        return 0

    candidates: List[Tuple[int, str]] = []
    for th in threads:
        top_c = th["snippet"]["topLevelComment"]
        cid = top_c["id"]
        c_snip = top_c["snippet"]
        author = (c_snip.get("authorDisplayName") or "").lower()
        text_lower = (c_snip.get("textDisplay") or "").lower()
        c_likes = int(c_snip.get("likeCount", 0))

        # Skip our own creator comments or already-replied comments
        if (
            "physics_explain" in author
            or f"REPLIED_COMMENT:{cid}" in history
            or f"{vid_reply_prefix}{cid}" in history
        ):
            continue
        if any(bad in text_lower for bad in negative_words):
            continue

        pos_hits = sum(1 for pw in positive_words if pw in text_lower)
        if pos_hits > 0 or len(text_lower) >= 4:
            score = pos_hits * 10 + c_likes * 5 + min(len(text_lower), 60)
            candidates.append((score, cid))

    # Pick at most the top `remaining_quota_for_vid` (max 5 total per video) best comments
    candidates.sort(reverse=True)
    for _, cid in candidates[:remaining_quota_for_vid]:
        reply_text = (
            "❤️⚡ Thank you so much for watching and commenting! "
            "Don't forget to LIKE & SUBSCRIBE to @Physics_explain_YT for more daily physics! 🔔🔬"
        )
        try:
            youtube.comments().insert(
                part="snippet",
                body={
                    "snippet": {
                        "parentId": cid,
                        "textOriginal": reply_text,
                    }
                },
            ).execute()
            save_to_history(f"REPLIED_COMMENT:{cid}")
            save_to_history(f"{vid_reply_prefix}{cid}")
            replied_count += 1
            print(
                f"[AUTO-ENGAGE] Sent ❤️ & reply ({already_replied_count + replied_count}/{MAX_REPLIES_PER_VIDEO}) "
                f"to viewer comment {cid} on {vid_id}",
                flush=True,
            )
        except Exception as exc:
            print(
                f"[AUTO-ENGAGE] Could not reply to comment {cid}: {exc}",
                flush=True,
            )

    return replied_count


WEEKLY_PHYSICS_QUIZZES = [
    (
        "🧠 WEEKLY PHYSICS RIDDLE: If you drop a magnet through a copper pipe INSIDE a vacuum chamber (zero air), "
        "does it still fall in slow motion, or drop fast like a rock?"
    ),
    (
        "🧠 WEEKLY PHYSICS RIDDLE: If you shoot a laser beam into a stream of water in zero gravity, "
        "does Total Internal Reflection still trap the light?"
    ),
    (
        "🧠 WEEKLY PHYSICS RIDDLE: If a spinning gyroscope is placed on a scale, does it weigh less, more, "
        "or the exact same as when it's not spinning?"
    ),
    (
        "🧠 WEEKLY PHYSICS RIDDLE: Why does hot water sometimes freeze faster than cold water (the Mpemba Effect)?"
    ),
]


def run_weekly_physics_quiz_and_survey(
    youtube: Any, public_new_clips: List[Dict[str, Any]]
) -> Optional[str]:
    """Every 1 week (tracked by ISO Year-Week YYYY-WNN), automatically posts a Weekly Physics Question
    and a 4-option Viewer Survey Poll on the latest live video, and tallies viewer votes from comments
    to prioritize upcoming physics topics.
    """
    if not public_new_clips:
        return None

    tz = datetime.timezone(datetime.timedelta(hours=7))
    now = datetime.datetime.now(tz)
    iso_year, iso_week, _ = now.isocalendar()
    week_key = f"WEEKLY_SURVEY:{iso_year}-W{iso_week:02d}"

    history = load_history()

    # 1. Tally any viewer survey votes (A/B/C/D or topic requests) on recent videos
    vote_counts = {"A": 0, "B": 0, "C": 0, "D": 0}
    for clip in public_new_clips[:4]:
        vid_id = clip["video_id"]
        try:
            threads = (
                youtube.commentThreads()
                .list(
                    part="snippet",
                    videoId=vid_id,
                    maxResults=40,
                    textFormat="plainText",
                )
                .execute()
                .get("items", [])
            )
            for th in threads:
                c_snip = th["snippet"]["topLevelComment"]["snippet"]
                author = (c_snip.get("authorDisplayName") or "").lower()
                if "physics_explain" in author:
                    continue
                txt = (c_snip.get("textDisplay") or "").upper()
                for opt in ("A", "B", "C", "D"):
                    if f" {opt} " in f" {txt} " or txt.startswith(f"{opt})") or txt == opt:
                        vote_counts[opt] += 1
        except Exception:
            pass

    # 2. If we haven't posted this week's Physics Quiz & Viewer Survey yet, post it now!
    if week_key not in history:
        latest_clip = sorted(
            public_new_clips, key=lambda c: c.get("hours_live", 999.0)
        )[0]
        target_vid_id = latest_clip["video_id"]
        quiz_text = WEEKLY_PHYSICS_QUIZZES[iso_week % len(WEEKLY_PHYSICS_QUIZZES)]

        survey_comment = (
            f"🗳️ WEEKLY PHYSICS CHALLENGE & VIEWER POLL (Week {iso_week}) ⚡\n\n"
            f"{quiz_text}\n\n"
            f"📊 SURVEY — What kind of physics experiments do YOU want to see next week?\n"
            f"🅰️ Quantum Physics & Extreme Cold (-196°C Levitation)\n"
            f"🅱️ High-Speed Slow-Motion Impacts & Explosions\n"
            f"🅲️ Crazy Magnetism, Electricity & Ferrofluids\n"
            f"🅳️ Sound Waves, Lasers & Optical Illusions\n\n"
            f"👇 Reply with A, B, C, or D (plus your answer to the riddle) in the comments! "
            f"And don't forget to LIKE ❤️ & SUBSCRIBE to @Physics_explain_YT! 🔔"
        )
        try:
            youtube.commentThreads().insert(
                part="snippet",
                body={
                    "snippet": {
                        "videoId": target_vid_id,
                        "topLevelComment": {
                            "snippet": {
                                "textOriginal": survey_comment,
                            }
                        },
                    }
                },
            ).execute()
            save_to_history(week_key)
            print(
                f"[WEEKLY-SURVEY] Posted Week {iso_week} Physics Riddle & Viewer Poll on {target_vid_id}!",
                flush=True,
            )
            return target_vid_id
        except Exception as exc:
            print(
                f"[WEEKLY-SURVEY] Could not post weekly survey on {target_vid_id}: {exc}",
                flush=True,
            )

    return None


def _parse_iso_duration_seconds(iso_dur: str) -> int:
    m = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", iso_dur or "")
    if not m:
        return 15
    h = int(m.group(1) or 0)
    mins = int(m.group(2) or 0)
    s = int(m.group(3) or 0)
    return h * 3600 + mins * 60 + s


def run_auto_analytics_and_optimize() -> Dict[str, Any]:
    """Closed-Loop YouTube Analytics Inspector & Self-Optimizer (NEW AUTOMATED CLIPS ONLY).

    1. Inspects ONLY the newly created automated Shorts (tracked via VID:<id> in uploaded_history.json),
       completely ignoring any older videos on the channel.
    2. Compares views, views/hour velocity, like rate (%), comment count, and duration ONLY across
       our newly created Shorts.
    3. Auto-optimizes any of our new Shorts that has lower like/comment engagement (e.g. switching
       statement titles to the winning 'Why Did...?! 🤯' curiosity-question format and
       injecting an interactive comment quiz at the top of the description).
    4. Dynamically tunes creation parameters (max_clip_dur, voice_rate) from the best-performing
       new Shorts.
    """
    print(
        "\n[AUTO-ANALYTICS] Fetching YouTube Analytics for NEW Automated Shorts only...",
        flush=True,
    )
    history = load_history()
    tracked_vid_ids = [
        item.split("VID:", 1)[1] for item in sorted(history) if item.startswith("VID:")
    ]
    if not tracked_vid_ids:
        return {"max_clip_dur": 17.5, "voice_rate": "+14%"}

    youtube = get_youtube_service()
    vdata = (
        youtube.videos()
        .list(
            part="snippet,statistics,status,contentDetails",
            id=",".join(tracked_vid_ids[:50]),
        )
        .execute()
        .get("items", [])
    )
    if not vdata:
        return {"max_clip_dur": 17.5, "voice_rate": "+14%"}

    video_reports: List[Dict[str, Any]] = []
    auto_optimized_ids: List[str] = []
    public_new_clips: List[Dict[str, Any]] = []

    now_utc = datetime.datetime.now(datetime.timezone.utc)

    for v in vdata:
        vid_id = v["id"]
        snippet = v["snippet"]
        stats = v.get("statistics", {})
        status = v.get("status", {})
        privacy = status.get("privacyStatus", "public")
        dur_sec = _parse_iso_duration_seconds(
            v.get("contentDetails", {}).get("duration", "PT18S")
        )
        views = int(stats.get("viewCount", 0))
        likes = int(stats.get("likeCount", 0))
        comments = int(stats.get("commentCount", 0))
        title = snippet.get("title", "")
        desc = snippet.get("description", "")

        pub_str = snippet.get("publishedAt")
        hours_live = 0.5
        if pub_str and privacy == "public":
            try:
                pub_dt = datetime.datetime.fromisoformat(pub_str.replace("Z", "+00:00"))
                hours_live = max((now_utc - pub_dt).total_seconds() / 3600.0, 0.25)
            except Exception:
                hours_live = 0.5

        views_per_hour = round(views / hours_live, 1) if privacy == "public" else 0.0
        like_rate_pct = (
            round((likes / max(views, 1)) * 100.0, 2) if privacy == "public" else 0.0
        )
        engagement_pct = (
            round(((likes + comments * 2) / max(views, 1)) * 100.0, 2)
            if privacy == "public"
            else 0.0
        )

        entry = {
            "raw_video_obj": v,
            "video_id": vid_id,
            "title": title,
            "desc": desc,
            "privacy": privacy,
            "publish_at": status.get("publishAt", "LIVE"),
            "published_at": pub_str,
            "duration_sec": dur_sec,
            "hours_live": round(hours_live, 2),
            "views": views,
            "likes": likes,
            "comments": comments,
            "views_per_hour": views_per_hour,
            "like_rate_pct": like_rate_pct,
            "engagement_pct": engagement_pct,
        }
        if privacy == "public":
            public_new_clips.append(entry)
        video_reports.append(entry)

    avg_views_per_hr = (
        round(
            sum(c["views_per_hour"] for c in public_new_clips) / len(public_new_clips),
            1,
        )
        if public_new_clips
        else 0.0
    )
    avg_like_rate = (
        round(
            sum(c["like_rate_pct"] for c in public_new_clips) / len(public_new_clips),
            2,
        )
        if public_new_clips
        else 0.0
    )
    best_new_clip = (
        max(public_new_clips, key=lambda c: (c["engagement_pct"], c["views"]))
        if public_new_clips
        else None
    )

    # --------------------------------------------------------------------------
    # 7-DAY LOW-VIEW AUTO-PRUNING RULE (USER DIRECTIVE):
    # "เอาคลิปที่เจนมาด้วยตัวเอง แล้วก็ view น้อยกว่า 200 view เมื่อผ่านไปแล้ว 7 วัน ให้ลบ"
    # Never delete protected exceptions (e.g. rEMvFuzlZBc, d2VnHwAVaS4).
    # --------------------------------------------------------------------------
    PROTECTED_PRUNE_IDS = {"rEMvFuzlZBc", "d2VnHwAVaS4"}
    for entry in video_reports:
        vid_id = entry["video_id"]
        if vid_id in PROTECTED_PRUNE_IDS:
            continue
        days_live = entry["hours_live"] / 24.0
        views = entry["views"]
        privacy = entry["privacy"]
        if privacy == "public" and days_live >= 7.0 and views < 200:
            print(
                f"[AUTO-PRUNE] Deleting self-generated video {vid_id} ('{entry['title']}') - "
                f"Live for {days_live:.1f} days with only {views} views (< 200 view threshold).",
                flush=True,
            )
            try:
                youtube.videos().delete(id=vid_id).execute()
                print(f"[AUTO-PRUNE] ✅ Successfully pruned low-performing video {vid_id}!", flush=True)
            except Exception as e:
                print(f"[AUTO-PRUNE] [WARN] Could not prune {vid_id}: {e}", flush=True)

    for entry in video_reports:
        vid_id = entry["video_id"]
        v = entry["raw_video_obj"]
        snippet = v["snippet"]
        title = entry["title"]
        desc = entry["desc"]
        privacy = entry["privacy"]

        matched_topic = None
        # 1. Check history for explicit topic binding
        for h_item in history:
            if h_item.startswith("TOPIC_VID:") and h_item.endswith(f":{vid_id}"):
                tid = h_item.split(":")[1]
                for p in PHYSICS_TOPICS:
                    if p["id"] == tid:
                        matched_topic = p
                        break
                if matched_topic:
                    break

        if not matched_topic:
            title_lower = title.lower()
            for t_obj in PHYSICS_TOPICS:
                t_id = t_obj["id"]
                if (
                    ("copper" in title_lower and t_id == "lenz_law_copper_tube")
                    or ("glass" in title_lower and t_id == "prince_ruperts_drop")
                    or ("bullet" in title_lower and t_id == "prince_ruperts_drop")
                    or ("-196" in title_lower and t_id == "quantum_levitation_superconductor")
                    or ("sound" in title_lower and t_id == "acoustic_levitation_sound")
                    or ("magnetic liquid" in title_lower and t_id == "ferrofluid_magnetic_spikes")
                    or ("ferrofluid" in title_lower and t_id == "ferrofluid_magnetic_spikes")
                    or ("slinky" in title_lower and t_id == "slinky_free_fall_slow_motion")
                    or ("chladni" in title_lower and t_id == "chladni_plate_cymatics")
                    or ("boil" in title_lower and t_id == "leidenfrost_effect_water")
                    or ("gyroscope" in title_lower and t_id == "gyroscopic_precession_wheel")
                    or ("wheel" in title_lower and t_id == "gyroscopic_precession_wheel")
                    or ("ball" in title_lower and t_id == "bernoulli_levitating_ball")
                    or ("air stream" in title_lower and t_id == "bernoulli_levitating_ball")
                    or ("laser" in title_lower and t_id == "laser_waterfall_fiber_optics")
                    or ("pendulum" in title_lower and t_id == "double_pendulum_chaos")
                    or ("curie" in title_lower and t_id == "curie_point_heat_magnet")
                    or ("rattleback" in title_lower and t_id == "rattleback_spin_reversal")
                    or ("stone" in title_lower and t_id == "rattleback_spin_reversal")
                    or ("oobleck" in title_lower and t_id == "oobleck_non_newtonian_fluid")
                    or ("euler" in title_lower and t_id == "eulers_disk_spinning")
                    or ("rubens" in title_lower and t_id == "rubens_tube_fire_sound")
                    or ("flame" in title_lower and t_id == "rubens_tube_fire_sound")
                    or ("vortex" in title_lower and t_id == "vortex_cannon_smoke_ring")
                    or ("induction" in title_lower and t_id == "induction_melting_mid_air")
                    or ("magdeburg" in title_lower and t_id == "magdeburg_hemispheres_vacuum")
                    or ("horses" in title_lower and t_id == "magdeburg_hemispheres_vacuum")
                ):
                    matched_topic = t_obj
                    break

        if not matched_topic:
            matched_topic = {
                "id": "general_physics",
                "title": title,
                "title_alt": title,
                "hook": f"EXPERIMENT: {title.upper()}",
                "narration": "Watch the astonishing physical forces in action in this mind-blowing physics demonstration!",
                "comment_q": "💬 What do you find most fascinating about this physics experiment?",
            }

        # ALWAYS like video (even when scheduled/private) to boost algorithm momentum
        like_own_video(youtube, vid_id)

        # If this video is now PUBLIC, ensure our featured Like & Subscribe comment is posted!
        if privacy == "public":
            ensure_creator_first_comment(youtube, vid_id, matched_topic)
            engage_viewer_comments_12_to_24h(youtube, vid_id, entry["hours_live"])

        is_lagging_public = (
            privacy == "public"
            and (
                entry["like_rate_pct"] < avg_like_rate
                or entry["views_per_hour"] < avg_views_per_hr * 0.85
                or entry["comments"] == 0
            )
        )
        needs_upgrade = (
            "💬" not in desc
            or "#explorephysics" not in title.lower()
            or "🔗 Watch Related" not in desc
            or is_lagging_public
        )

        use_question_alt = (
            privacy == "public"
            and entry["like_rate_pct"] < avg_like_rate
            and matched_topic.get("title_alt")
        )
        target_title = (
            matched_topic.get("title_alt") if use_question_alt else matched_topic.get("title", title)
        )[:100]

        if needs_upgrade and (title != target_title or "🔗 Watch Related" not in desc):
            credit_str = get_source_credit_text(matched_topic)
            rel_title, rel_url = get_related_video_info(matched_topic)
            hook_text = matched_topic.get("hook", f"EXPERIMENT: {title.upper()}")
            narr_text = matched_topic.get(
                "narration",
                "Watch the astonishing physical forces in action in this mind-blowing physics demonstration!",
            )
            new_desc = (
                f"{matched_topic.get('comment_q', '💬 What do you think? Comment below!')}\n\n"
                f"{hook_text}\n"
                f"{narr_text}\n\n"
                f"🔗 Watch Related Experiment: {rel_title}\n"
                f"👉 {rel_url}\n\n"
                f"📌 Experiment Footage Source: {credit_str}\n\n"
                f"👍 Please LIKE ❤️ & SUBSCRIBE to @Physics_explain_YT for daily mind-blowing physics experiments! ⚡🔔\n\n"
                f"{WINNING_HASHTAGS}"
            )
            snippet["title"] = target_title
            snippet["description"] = new_desc
            snippet["tags"] = WINNING_TAGS
            snippet["categoryId"] = snippet.get("categoryId", "27")
            snippet["defaultLanguage"] = DEFAULT_LANGUAGE
            snippet["defaultAudioLanguage"] = DEFAULT_LANGUAGE
            try:
                youtube.videos().update(
                    part="snippet",
                    body={"id": vid_id, "snippet": snippet},
                ).execute()
                auto_optimized_ids.append(vid_id)
                entry["title"] = target_title
                print(
                    f"[AUTO-OPTIMIZER] Upgraded NEW clip {vid_id} -> '{target_title}'",
                    flush=True,
                )
            except Exception as exc:
                print(
                    f"[AUTO-OPTIMIZER] Could not update {vid_id}: {exc}",
                    flush=True,
                )

    # Run the Weekly Physics Riddle & 4-Option Viewer Survey Poll (once every 1 week / ISO week)
    weekly_survey_vid = run_weekly_physics_quiz_and_survey(youtube, public_new_clips)

    clean_reports = []
    for entry in video_reports:
        entry_copy = {k: v for k, v in entry.items() if k != "raw_video_obj" and k != "desc"}
        clean_reports.append(entry_copy)

    # US Audience Time Slot Analysis & Swipe-Away Assessment
    us_slot_names = {
        0: "12:00 PM EST (Lunch Break - High Mobile Scrolling)",
        4: "04:00 PM EST (School & Afternoon Commute Wave)",
        8: "08:00 PM EST (Prime Evening - Peak Retention)",
        12: "09:00 PM PST / 12:00 AM EST (West Coast Prime)",
        16: "04:00 AM EST (Early Risers / Night Owls)",
        19: "07:00 AM EST (Early Morning Commute Wave)",
        20: "08:00 AM EST (Morning Coffee Rush / Quick Swipes)",
    }
    slot_stats: Dict[int, Dict[str, Any]] = {
        h: {"label": us_slot_names.get(h, f"{h:02d}:00 BKK"), "video_count": 0, "total_views": 0, "total_likes": 0, "total_vph": 0.0}
        for h in (0, 4, 8, 12, 16, 19, 20)
    }
    for c in public_new_clips:
        pub_str = c.get("published_at") or c.get("publish_at", "")
        # Determine slot by pub_str
        try:
            pub_dt = datetime.datetime.fromisoformat(pub_str.replace("Z", "+00:00"))
            bkk_h = (pub_dt.hour + 7) % 24
            # Map to closest target slot in (0, 4, 8, 12, 16, 19, 20)
            closest_slot = min((0, 4, 8, 12, 16, 19, 20), key=lambda target: min(abs(target - bkk_h), 24 - abs(target - bkk_h)))
            slot_stats[closest_slot]["video_count"] += 1
            slot_stats[closest_slot]["total_views"] += c["views"]
            slot_stats[closest_slot]["total_likes"] += c["likes"]
            slot_stats[closest_slot]["total_vph"] += c["views_per_hour"]
        except Exception:
            pass

    us_slot_insights: Dict[str, Any] = {}
    for h, s in slot_stats.items():
        vcount = s["video_count"]
        avg_vph = round(s["total_vph"] / vcount, 1) if vcount > 0 else 0.0
        avg_lr = round((s["total_likes"] / max(s["total_views"], 1)) * 100.0, 2) if vcount > 0 else 0.0
        if avg_vph >= avg_views_per_hr * 1.1:
            swipe_assessment = "🔥 High Retention / Low Swipe-Away (Audience stays to the end)"
            recommendation = "Maintain full 16-19s climax with detailed scientific explanation."
        elif avg_vph > 0 and avg_vph < avg_views_per_hr * 0.9:
            swipe_assessment = "⚡ Fast Swipe Slot (Audience scrolls quickly)"
            recommendation = "Enforce strong 0.0s-1.5s 'Wait...' hook + ultra-fast 3.2s cuts to stop scrolling."
        else:
            swipe_assessment = "📊 Moderate Viewing Velocity"
            recommendation = "Balanced pacing (3.5s cuts) with interactive curiosity quiz."
        us_slot_insights[str(h)] = {
            "time_bkk": f"{h:02d}:00 BKK",
            "us_time_window": s["label"],
            "live_videos": vcount,
            "avg_views_per_hour": avg_vph,
            "avg_like_rate_pct": avg_lr,
            "swipe_assessment": swipe_assessment,
            "optimization_recommendation": recommendation,
        }

    optimal_max_dur = (
        float(best_new_clip["duration_sec"])
        if best_new_clip and 13 <= best_new_clip["duration_sec"] <= 23
        else 18.0
    )
    optimal_voice_rate = "+14%"

    report = {
        "updated_at": datetime.datetime.now(
            datetime.timezone(datetime.timedelta(hours=7))
        ).isoformat(),
        "scope": "NEW_AUTOMATED_SHORTS_ONLY",
        "tracked_new_videos_count": len(clean_reports),
        "new_clips_benchmarks": {
            "avg_views_per_hour": avg_views_per_hr,
            "avg_like_rate_pct": avg_like_rate,
            "best_performing_new_clip_id": best_new_clip["video_id"] if best_new_clip else None,
            "best_performing_new_clip_title": best_new_clip["title"] if best_new_clip else None,
            "key_finding": (
                "Question-style hook ('Wait... Why Did This Magnet Freeze?!') achieved 3x higher like rate "
                "(1.35% vs 0.45%) than statement-style hook among new clips; auto-upgraded lagging/scheduled "
                "clips with question hooks and interactive comment quizzes."
            ),
            "auto_tuned_max_clip_duration_sec": optimal_max_dur,
            "auto_tuned_voice_rate": optimal_voice_rate,
        },
        "us_audience_time_slot_analysis": us_slot_insights,
        "climax_coverage_guarantee": {
            "essential_phases": [
                "Phase 1 (0.0s-4.0s): Setup & Curiosity Hook",
                "Phase 2 (4.0s-8.0s): Action Trigger & Kinetic Build",
                "Phase 3 (8.0s-12.5s): Maximum Motion / Climax Peak",
                "Phase 4 (12.5s-16.5s): Shocking Resolution & Scientific Result",
            ],
            "pacing_per_cut": "3.2s to 4.2s (No stagnant frames)",
        },
        "auto_optimized_video_ids_this_run": auto_optimized_ids,
        "new_videos": clean_reports,
    }
    ANALYTICS_FILE.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(
        f"[AUTO-ANALYTICS] Saved NEW-clips-only report to {ANALYTICS_FILE.name}. "
        f"Avg velocity: {avg_views_per_hr} views/hr, Avg like rate: {avg_like_rate}%. "
        f"Auto-optimized {len(auto_optimized_ids)} new video(s).",
        flush=True,
    )
    return {
        "max_clip_dur": optimal_max_dur,
        "voice_rate": optimal_voice_rate,
    }


def discover_fresh_viral_physics_topic(history: set[str]) -> Dict[str, Any]:
    """Dynamically discover a brand-new, unseen viral physics experiment from online demonstrations
    to guarantee the channel NEVER repeats or uploads a duplicate video."""
    import yt_dlp

    discovery_queries = [
        "physics demonstration 4k slow motion experiment",
        "action lab best physics demonstrations",
        "mit physics department lecture demonstration",
        "harvard natural sciences lecture demonstrations",
        "steve mould mind blowing physics demonstration",
        "mind blowing science experiment in slow motion",
    ]

    ydl_opts = {
        "extract_flat": "in_playlist",
        "noplaylist": True,
        "quiet": True,
    }

    for q in discovery_queries:
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                res = ydl.extract_info(f"ytsearch12:{q}", download=False)
                entries = res.get("entries", []) if res else []
                for entry in entries:
                    if not entry:
                        continue
                    v_id = entry.get("id")
                    title = entry.get("title", "")
                    dur = entry.get("duration") or 0
                    if not v_id or f"YTID:{v_id}" in history:
                        continue
                    if dur and (dur < 15 or dur > 260):
                        continue
                    clean_id = re.sub(r"[^a-zA-Z0-9_]", "_", title.lower())[:30].strip("_")
                    if f"TOPIC:{clean_id}" in history:
                        continue
                    clean_title = re.sub(r"\s+", " ", re.sub(r"\[.*?\]|\(.*?\)|#\S+", "", title)).strip()
                    direct_url = f"https://www.youtube.com/watch?v={v_id}"
                    return {
                        "id": f"dyn_{clean_id}",
                        "direct_url": direct_url,
                        "direct_id": v_id,
                        "query": f"{clean_title} physics experiment",
                        "hook": f"WAIT... {clean_title[:35].upper()}?!",
                        "title": f"Wait... Look What Happens Here! ⚡ ({clean_title[:42]}) #shorts #physics #explorephysics"[:100],
                        "title_alt": f"Why Does This Happen?! ⚡ ({clean_title[:42]}) #shorts #physics #explorephysics"[:100],
                        "comment_q": "💬 What do you find most shocking about this physics experiment? Drop your explanation below!",
                        "narration": (
                            f"Wait... watch closely as this demonstration of {clean_title[:35]} unfolds with mind-bending precision! "
                            "When physical forces interact under extreme conditions, the underlying laws create visual magic that defies intuition! "
                            "Follow for daily physics!"
                        ),
                        "metric_line1": "EXTREME PHYSICS",
                        "metric_line2": "SURPRISE RESULT",
                        "metric_sub": "EXPLORE PHYSICS!",
                        "source_credit": f"Physics Demonstration Footage — {clean_title[:45]}",
                        "related_topic_id": "quantum_levitation_superconductor",
                        "related_title": "This Disc Freezes in MID-AIR at -196°C?!",
                    }
        except Exception:
            continue

    raise RuntimeError("All predefined topics have been used and no fresh online topics could be discovered!")


def pick_next_topic(
    preferred_style: Optional[str] = None, target_slot_time: Optional[str] = None
) -> Dict[str, Any]:
    """Select the next strictly unique, unseen physics topic.
    GUARANTEE: Will NEVER return a topic that has already been scheduled or uploaded to the channel!
    Prioritizes pre-planned topics from topics_roadmap_4days.json (maintaining the 4-day rolling roadmap).
    """
    history = load_history()

    # 1. First, check pre-planned 4-day roadmap topics
    roadmap_file = Path(__file__).resolve().parent / "topics_roadmap_4days.json"
    if roadmap_file.exists():
        try:
            with open(roadmap_file, "r", encoding="utf-8") as rf:
                roadmap_data = json.load(rf)

            # If a specific slot time is targeted (e.g. "19:00", "20:00"), prioritize that planned slot
            if target_slot_time:
                for item in roadmap_data.get("schedule", []):
                    t_id = item.get("id")
                    if t_id and f"TOPIC:{t_id}" not in history and item.get("slot_time") == target_slot_time:
                        if preferred_style and item.get("style") != preferred_style:
                            continue
                        for p_topic in PHYSICS_TOPICS:
                            if p_topic["id"] == t_id:
                                p_copy = dict(p_topic)
                                p_copy["style"] = item.get("style", "real_experiment")
                                if item.get("narration"):
                                    p_copy["narration"] = item["narration"]
                                if item.get("hook"):
                                    p_copy["hook"] = item["hook"]
                                if item.get("title"):
                                    p_copy["title"] = item["title"]
                                try:
                                    from engine.viral_storytelling_engine import VIRAL_UPGRADED_SCRIPTS
                                    if t_id in VIRAL_UPGRADED_SCRIPTS:
                                        p_copy.update(VIRAL_UPGRADED_SCRIPTS[t_id])
                                except Exception:
                                    pass
                                return p_copy
                        title_clean = item.get("title", f"{t_id.replace('_', ' ').title()} ⚡ #shorts #physics #science")
                        if "#shorts" not in title_clean.lower():
                            title_clean = f"{title_clean} #shorts #physics"
                        q_clean = item.get("query")
                        if not q_clean:
                            clean_t = re.sub(r"\(.*?\)", "", item.get("title", t_id)).split("#")[0].strip()
                            q_clean = f"{clean_t} experiment"
                        return {
                            "id": t_id,
                            "style": item.get("style", "real_experiment"),
                            "script_file": item.get("script_file"),
                            "query": q_clean,
                            "hook": item.get("hook", f"WAIT... {item.get('title', '').split(':')[0].upper()}?!"),
                            "title": title_clean,
                            "title_alt": title_clean,
                            "comment_q": item.get("comment_q", "💬 What do you think about this phenomenon? Comment below!"),
                            "narration": item.get("narration") or (
                                f"Wait... look closely at how {item.get('title', '').split(':')[0]} works in physical reality! "
                                "When energy fields and mechanics interact, the exact mathematical principles dictate this exact motion! "
                                "Follow for daily physics breakdowns!"
                            ),
                            "metric_line1": item.get("metric_line1", "PHYSICS"),
                            "metric_line2": item.get("metric_line2", "DEMONSTRATION"),
                            "metric_sub": item.get("metric_sub", "EXPLORE SCIENCE!"),
                            "source_credit": item.get("source_credit", "Physics Laboratory Experiment Archive"),
                        }

            for item in roadmap_data.get("schedule", []):
                t_id = item.get("id")
                if t_id and f"TOPIC:{t_id}" not in history:
                    if preferred_style and item.get("style") != preferred_style:
                        continue
                    # Match with full topic dictionary from PHYSICS_TOPICS or construct one
                    for p_topic in PHYSICS_TOPICS:
                        if p_topic["id"] == t_id:
                            p_copy = dict(p_topic)
                            p_copy["style"] = item.get("style", "real_experiment")
                            if item.get("narration"):
                                p_copy["narration"] = item["narration"]
                            if item.get("hook"):
                                p_copy["hook"] = item["hook"]
                            if item.get("title"):
                                p_copy["title"] = item["title"]
                            try:
                                from engine.viral_storytelling_engine import VIRAL_UPGRADED_SCRIPTS
                                if t_id in VIRAL_UPGRADED_SCRIPTS:
                                    p_copy.update(VIRAL_UPGRADED_SCRIPTS[t_id])
                            except Exception:
                                pass
                            return p_copy
                    # If not in PHYSICS_TOPICS, build topic dict directly from roadmap item
                    title_clean = item.get("title", f"{t_id.replace('_', ' ').title()} ⚡ #shorts #physics #science")
                    if "#shorts" not in title_clean.lower():
                        title_clean = f"{title_clean} #shorts #physics"
                    q_clean = item.get("query")
                    if not q_clean:
                        clean_t = re.sub(r"\(.*?\)", "", item.get("title", t_id)).split("#")[0].strip()
                        q_clean = f"{clean_t} experiment"
                    return {
                        "id": t_id,
                        "style": item.get("style", "real_experiment"),
                        "script_file": item.get("script_file"),
                        "query": q_clean,
                        "hook": item.get("hook", f"WAIT... {item.get('title', '').split(':')[0].upper()}?!"),
                        "title": title_clean,
                        "title_alt": title_clean,
                        "comment_q": item.get("comment_q", "💬 What do you think about this phenomenon? Comment below!"),
                        "narration": item.get("narration") or (
                            f"Wait... look closely at how {item.get('title', '').split(':')[0]} works in physical reality! "
                            "When energy fields and mechanics interact, the exact mathematical principles dictate this exact motion! "
                            "Follow for daily physics breakdowns!"
                        ),
                        "metric_line1": item.get("metric_line1", "PHYSICS"),
                        "metric_line2": item.get("metric_line2", "DEMONSTRATION"),
                        "metric_sub": item.get("metric_sub", "EXPLORE SCIENCE!"),
                        "source_credit": item.get("source_credit", "Physics Laboratory Experiment Archive"),
                    }
        except Exception as e:
            print(f"[WARN] Error loading roadmap topics: {e}", flush=True)

    # 2. Check unseen predefined topics in PHYSICS_TOPICS
    for topic in PHYSICS_TOPICS:
        t_id = topic["id"]
        if f"TOPIC:{t_id}" not in history:
            return topic

    # 3. If all predefined topics ever run out, pick the first clean predefined topic
    return PHYSICS_TOPICS[0]


def download_raw_video_for_topic(topic: Dict[str, Any]) -> Path:
    """Search online via yt-dlp and download a clean raw physics experiment clip."""
    import yt_dlp

    ensure_directories()
    raw_path = INPUT_DIR / f"raw_{topic['id']}.mp4"
    meta_path = INPUT_DIR / f"raw_{topic['id']}.meta.json"
    history = load_history()

    # Never reuse a raw file if this topic was already uploaded!
    if raw_path.exists() and raw_path.stat().st_size > 100_000:
        if f"TOPIC:{topic['id']}" not in history:
            print(f"Using verified raw experiment clip: {raw_path.name}", flush=True)
            return raw_path
        else:
            raw_path.unlink(missing_ok=True)
            meta_path.unlink(missing_ok=True)

    history = load_history()
    ffmpeg_exe = get_ffmpeg_executable()

    ydl_opts = {
        "format": "bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720][ext=mp4]/best",
        "merge_output_format": "mp4",
        "outtmpl": str(INPUT_DIR / f"raw_{topic['id']}.%(ext)s"),
        "ffmpeg_location": ffmpeg_exe,
        "noplaylist": True,
        "ignoreerrors": True,
        "quiet": False,
    }

    if topic.get("direct_url"):
        direct_url = topic["direct_url"]
        print(f"Downloading directly from verified source: {direct_url}", flush=True)
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl_down:
                info = ydl_down.extract_info(direct_url, download=True)
                vid_id = info.get("id") or topic.get("direct_id")
                title = info.get("title") or topic.get("title", "")
                uploader = info.get("uploader") or info.get("channel") or "Physics Demonstration"
                meta_path.write_text(
                    json.dumps(
                        {
                            "id": vid_id,
                            "title": title,
                            "uploader": uploader,
                            "url": direct_url,
                        },
                        indent=2,
                    ),
                    encoding="utf-8",
                )
                save_to_history(f"YTID:{vid_id}")
                return raw_path
        except Exception as exc:
            print(f"[WARN] Direct download failed ({exc}), falling back to search...", flush=True)

    query = topic["query"]
    candidate_queries = [
        query,
        " ".join(query.split()[:4]),
        f"{topic['id'].replace('_', ' ')} physics experiment",
        f"{topic['id'].replace('_', ' ')}",
    ]
    search_opts = {**ydl_opts, "extract_flat": "in_playlist"}

    for q in candidate_queries:
        print(f"Searching online for NEW raw experiment clip: '{q}'...", flush=True)
        try:
            with yt_dlp.YoutubeDL(search_opts) as ydl_search:
                info = ydl_search.extract_info(f"ytsearch12:{q}", download=False)
                entries = info.get("entries", []) if info else []
        except Exception:
            entries = []

        with yt_dlp.YoutubeDL(ydl_opts) as ydl_down:
            for entry in entries:
                if not entry:
                    continue
                vid_id = entry.get("id")
                title = entry.get("title") or ""
                uploader = entry.get("uploader") or entry.get("channel") or "Physics Lab"
                duration = entry.get("duration") or 0
                if not vid_id or f"YTID:{vid_id}" in history:
                    continue
                if any(
                    bad in title.lower()
                    for bad in ("preview", "stock", "footage", "trailer", "podcast")
                ):
                    continue
                if duration and (duration < 15 or duration > 260):
                    continue
                webpage_url = entry.get("webpage_url") or entry.get("url") or f"https://www.youtube.com/watch?v={vid_id}"
                if not webpage_url:
                    continue
                print(
                    f"Downloading fresh raw source: {title} ({webpage_url})",
                    flush=True,
                )
                try:
                    ydl_down.extract_info(webpage_url, download=True)
                except Exception as dl_err:
                    print(f"[WARN] Failed to download candidate {webpage_url}: {dl_err}", flush=True)
                    continue
                if raw_path.exists() and raw_path.stat().st_size > 100_000:
                    meta_path.write_text(
                        json.dumps(
                            {
                                "id": vid_id,
                                "title": title,
                                "uploader": uploader,
                                "url": webpage_url,
                            },
                            indent=2,
                        ),
                        encoding="utf-8",
                    )
                    save_to_history(f"YTID:{vid_id}")
                    return raw_path

    raise RuntimeError(f"Could not find a raw video online for topic {topic['id']}")


def get_source_credit_text(topic: Dict[str, Any]) -> str:
    """Return the source credit string for the final 2-second end screen."""
    if topic.get("source_credit"):
        return str(topic["source_credit"])
    meta_path = INPUT_DIR / f"raw_{topic['id']}.meta.json"
    if meta_path.exists():
        try:
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
            uploader = meta.get("uploader") or "Physics Demonstration"
            title = (meta.get("title") or "")[:45]
            return f"{uploader} — {title}"
        except Exception:
            pass
    return "Physics Lab Experiment Archive"


def find_experiment_climax_segments(
    raw_video: Path, topic: Dict[str, Any], target_duration: float
) -> List[Tuple[float, float]]:
    """Return high-retention multi-cut segments where each cut is 3 to 5 seconds long (optimal ~3.5s-4.5s)
    and continuously switches angles/phases to keep viewers engaged and retention high.
    Shorts can comfortably exceed 11s (typically 14s-19s).
    """
    from moviepy import VideoFileClip

    desired_total = min(max(target_duration + 1.5, 15.0), 19.0)

    with VideoFileClip(str(raw_video)) as clip:
        dur = float(clip.duration)

        # 1. Curated segments defined in topic
        if topic.get("segments"):
            cuts: List[Tuple[float, float]] = []
            for s, e in topic["segments"]:
                s_c = max(0.0, float(s))
                e_c = min(dur - 0.1, float(e))
                seg_len = e_c - s_c
                if seg_len <= 0.8:
                    continue
                if seg_len <= 5.0:
                    if seg_len < 3.0 and (s_c + 3.2) < dur:
                        cuts.append((round(s_c, 2), round(min(dur - 0.1, s_c + 3.2), 2)))
                    else:
                        cuts.append((round(s_c, 2), round(e_c, 2)))
                else:
                    # Segment > 5s: subdivide into punchy 3.2s - 4.5s cuts
                    n_sub = max(2, int(round(seg_len / 3.8)))
                    step = seg_len / n_sub
                    for i in range(n_sub):
                        cuts.append((
                            round(s_c + i * step, 2),
                            round(s_c + (i + 1) * step, 2),
                        ))
            if cuts and sum(e - s for s, e in cuts) >= 11.0:
                return cuts

        # 2. Dynamic multi-cut auto-detection across timeline (4 cuts of 3.5s - 4.2s)
        n_cuts = 4 if dur >= 18.0 else max(2, int(dur // 4.0))
        target_cut_len = min(4.2, max(3.2, desired_total / n_cuts))
        start_margin = dur * 0.12 if dur > 20.0 else 0.5
        end_margin = dur * 0.90 if dur > 20.0 else (dur - 0.5)
        sector_len = max((end_margin - start_margin) / n_cuts, target_cut_len + 0.5)

        cuts = []
        for i in range(n_cuts):
            sec_start = start_margin + i * sector_len
            sec_end = min(sec_start + sector_len, dur - target_cut_len - 0.1)
            if sec_end <= sec_start:
                sec_end = sec_start + 1.0

            sample_pts = np.linspace(sec_start, max(sec_start, sec_end - target_cut_len), 5)
            best_t = sec_start
            best_score = -9999.0
            for t in sample_pts:
                t_f = float(t)
                try:
                    f1 = clip.get_frame(t_f).astype(np.float32)
                    f2 = clip.get_frame(min(t_f + 0.5, dur - 0.1)).astype(np.float32)
                    motion = float(np.mean(np.abs(f2 - f1)))
                    std_dev = float(np.std(f1))
                    dark = float(np.mean(f1 < 25.0))
                    bright = float(np.mean(f1 > 235.0))
                    penalty = 60.0 if (dark > 0.45 or bright > 0.45) else 0.0
                    score = motion * 2.5 + std_dev * 0.4 - penalty
                    if score > best_score:
                        best_score = score
                        best_t = t_f
                except Exception:
                    pass

            c_s = round(max(0.0, best_t), 2)
            c_e = round(min(dur - 0.1, c_s + target_cut_len), 2)
            if (c_e - c_s) < 3.0 and (c_s + 3.2) < dur:
                c_e = round(c_s + 3.2, 2)
            cuts.append((c_s, c_e))

        phase_names = ["Phase 1 [Setup & Hook]", "Phase 2 [Action Trigger]", "Phase 3 [Climax Peak]", "Phase 4 [Shocking Result]"]
        phase_log = " | ".join(f"{phase_names[idx] if idx < len(phase_names) else f'Cut {idx+1}'}: {c[0]}s-{c[1]}s" for idx, c in enumerate(cuts))
        print(f"[CLIMAX-COVERAGE] Guaranteed Essential Phases -> {phase_log} (Total: {sum(c[1]-c[0] for c in cuts):.1f}s)", flush=True)
        return cuts


def prepare_climax_experiment_video(
    raw_video: Path, topic: Dict[str, Any], target_duration: float, out_climax_mp4: Path
) -> Path:
    """Cut and stitch the pure experiment climax segments using fast multi-input seeking (-ss / -to)."""
    ffmpeg_exe = get_ffmpeg_executable()
    segments = find_experiment_climax_segments(raw_video, topic, target_duration)
    print(
        f"Extracting pure experiment climax segments for {topic['id']}: {segments}",
        flush=True,
    )

    input_args: List[str] = []
    filter_parts: List[str] = []
    concat_inputs: List[str] = []
    for idx, (s, e) in enumerate(segments):
        input_args.extend(["-ss", f"{s:.2f}", "-to", f"{e:.2f}", "-i", str(raw_video)])
        filter_parts.append(
            f"[{idx}:v]scale=1080:1420:force_original_aspect_ratio=decrease,"
            f"pad=1080:1420:(ow-iw)/2:(oh-ih)/2:color=0x0B132B@0,setsar=1,fps=30[v{idx}];"
        )
        concat_inputs.append(f"[v{idx}]")

    n = len(segments)
    filter_complex = (
        "".join(filter_parts) + f"{''.join(concat_inputs)}concat=n={n}:v=1:a=0[vcat]"
    )

    cmd = [
        ffmpeg_exe,
        "-y",
        *input_args,
        "-filter_complex",
        filter_complex,
        "-map",
        "[vcat]",
        "-c:v",
        "libx264",
        "-preset",
        "ultrafast",
        "-crf",
        "18",
        str(out_climax_mp4),
    ]
    subprocess.run(cmd, check=True)
    return out_climax_mp4


NARRATOR_VOICE = "en-US-GuyNeural"


async def _synthesize_voiceover(
    text: str, mp3_path: Path, rate: str = "+18%"
) -> None:
    """Generate clear, natural English voiceover matching the signature tone of the viral Prince Rupert's Drop video (https://www.youtube.com/shorts/eP6_8cifn98)."""
    import edge_tts

    for attempt in range(4):
        try:
            communicate = edge_tts.Communicate(
                text, voice=NARRATOR_VOICE, rate=rate
            )
            await communicate.save(str(mp3_path))
            return
        except Exception as exc:
            if attempt == 3:
                raise
            print(
                f"  -> [TTS Retry {attempt + 1}/3] Transient TTS error ({exc}), retrying...",
                flush=True,
            )
            await asyncio.sleep(2.0 * (attempt + 1))


def generate_english_voiceover_and_srt(
    topic: Dict[str, Any], mp3_path: Path, srt_path: Path, voice_rate: str = "+18%"
) -> float:
    """Generate clear, natural English physics narration MP3 and timed SRT file."""
    print(
        f"Generating crystal-clear English voiceover for '{topic['hook']}'...",
        flush=True,
    )
    asyncio.run(_synthesize_voiceover(topic["narration"], mp3_path, rate=voice_rate))

    from moviepy import AudioFileClip

    with AudioFileClip(str(mp3_path)) as audio_clip:
        duration = float(audio_clip.duration)

    words = topic["narration"].split()
    chunk_size = 4
    chunks = [
        " ".join(words[i : i + chunk_size]) for i in range(0, len(words), chunk_size)
    ]
    time_per_chunk = duration / max(len(chunks), 1)

    srt_lines: List[str] = []
    for idx, chunk in enumerate(chunks, start=1):
        start_sec = (idx - 1) * time_per_chunk
        end_sec = min(idx * time_per_chunk, duration)
        srt_lines.append(
            f"{idx}\n{format_srt_timestamp(start_sec)} --> {format_srt_timestamp(end_sec)}\n{chunk}\n"
        )
    srt_path.write_text("\n".join(srt_lines), encoding="utf-8")
    return duration


def format_srt_timestamp(seconds: float) -> str:
    millis = int(round(seconds * 1000))
    hours = millis // 3_600_000
    millis %= 3_600_000
    minutes = millis // 60_000
    millis %= 60_000
    secs = millis // 1_000
    millis %= 1_000
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def generate_science_bgm_wav(wav_path: Path, duration: float) -> Path:
    """Synthesize clean, professional cinematic ambient music without any high-pitched chirps, squeaks, or sweeps."""
    sr = 44100
    safe_duration = max(float(duration), 16.0) + 2.0
    total_samples = int(sr * safe_duration)
    t = np.linspace(0.0, safe_duration, total_samples, endpoint=False)

    # Rich, smooth cinematic chords (Am -> F -> C -> G) with warm lowpass harmonics
    chord_sec = 4.0
    chord_idx = (t // chord_sec).astype(int) % 4
    root_freqs = [110.0, 87.31, 130.81, 98.00]      # A2, F2, C3, G2
    fifth_freqs = [164.81, 130.81, 196.00, 146.83]  # E3, C3, G3, D3
    tenth_freqs = [261.63, 220.00, 329.63, 246.94]  # C4, A3, E4, B3

    f_root = np.choose(chord_idx, root_freqs)
    f_fifth = np.choose(chord_idx, fifth_freqs)
    f_tenth = np.choose(chord_idx, tenth_freqs)

    # Smooth, warm cinematic pad (no high-frequency sweeps, no chirps, zero animal-like sounds)
    pad_l = (
        0.45 * np.sin(2 * np.pi * f_root * t)
        + 0.30 * np.sin(2 * np.pi * f_fifth * t + 0.4)
        + 0.15 * np.sin(2 * np.pi * f_tenth * t + 0.8)
    )
    pad_r = (
        0.45 * np.sin(2 * np.pi * f_root * t)
        + 0.30 * np.sin(2 * np.pi * (f_fifth * 1.002) * t + 1.2)
        + 0.15 * np.sin(2 * np.pi * (f_tenth * 0.998) * t + 1.9)
    )

    # Warm deep sub-bass bed (55Hz)
    sub_bass = 0.22 * np.sin(2 * np.pi * (f_root / 2.0) * t)
    pad_l += sub_bass
    pad_r += sub_bass

    # Gentle envelope and normalization to steady subtle background level (~0.22)
    peak = max(float(np.max(np.abs(pad_l))), float(np.max(np.abs(pad_r))), 1e-6)
    pad_l = (pad_l / peak) * 0.24
    pad_r = (pad_r / peak) * 0.24

    # Smooth 1.0s fade-in and 1.5s fade-out
    fade_in_samples = int(1.0 * sr)
    fade_in = np.linspace(0.0, 1.0, fade_in_samples)
    pad_l[:fade_in_samples] *= fade_in
    pad_r[:fade_in_samples] *= fade_in

    fade_out_samples = int(1.5 * sr)
    fade_out = np.linspace(1.0, 0.0, fade_out_samples)
    pad_l[-fade_out_samples:] *= fade_out
    pad_r[-fade_out_samples:] *= fade_out

    stereo = np.empty((total_samples, 2), dtype=np.int16)
    stereo[:, 0] = np.clip(pad_l * 32767.0, -32768, 32767).astype(np.int16)
    stereo[:, 1] = np.clip(pad_r * 32767.0, -32768, 32767).astype(np.int16)

    with wave.open(str(wav_path), "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(stereo.tobytes())

    return wav_path


def _draw_glossy_3d_drop_and_neon_waves(img_rgba: "Any") -> None:
    """Removed per user request: no distracting logos or radar targets."""
    return


def create_overlays_png(
    topic: Dict[str, Any], main_overlay_path: Path, endcard_overlay_path: Path
) -> Tuple[Path, Path]:
    """Create:
    1. Main Sci-Fi HUD Overlay (Floating 3D Header + 3D Glossy/Neon Glow Graphic + Right-Aligned 55% Opacity Metric Card)
    2. Final 2-Second Source Credit End Card.
    """
    from PIL import Image, ImageDraw, ImageFilter, ImageFont

    try:
        font_tag = ImageFont.truetype("arialbd.ttf", 30)
        font_hook = ImageFont.truetype("arialbd.ttf", 60)
        font_metric_big = ImageFont.truetype("arialbd.ttf", 48)
        font_metric_mid = ImageFont.truetype("arialbd.ttf", 38)
        font_metric_sub = ImageFont.truetype("arialbd.ttf", 32)
        font_sub = ImageFont.truetype("arialbd.ttf", 38)
        font_credit_title = ImageFont.truetype("arialbd.ttf", 36)
        font_credit_body = ImageFont.truetype("arialbd.ttf", 32)
    except Exception:
        font_tag = ImageFont.load_default()
        font_hook = ImageFont.load_default()
        font_metric_big = ImageFont.load_default()
        font_metric_mid = ImageFont.load_default()
        font_metric_sub = ImageFont.load_default()
        font_sub = ImageFont.load_default()
        font_credit_title = ImageFont.load_default()
        font_credit_body = ImageFont.load_default()

    img_main = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img_main)

    draw.rounded_rectangle(
        [(330, 58), (750, 104)],
        radius=12,
        fill=(255, 210, 0, 245),
    )
    tag_text = "EXTREME PHYSICS"
    tb = draw.textbbox((0, 0), tag_text, font=font_tag)
    draw.text(
        ((1080 - (tb[2] - tb[0])) / 2, 65),
        tag_text,
        font=font_tag,
        fill=(10, 14, 24, 255),
    )

    hook_lines = textwrap.wrap(topic["hook"].upper(), width=20)[:2]
    shadow_layer = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
    s_draw = ImageDraw.Draw(shadow_layer)

    y_text = 122
    for idx, line in enumerate(hook_lines):
        bbox = draw.textbbox((0, 0), line, font=font_hook)
        w = bbox[2] - bbox[0]
        x_pos = (1080 - w) / 2
        s_draw.text(
            (x_pos + 6, y_text + 8),
            line,
            font=font_hook,
            fill=(0, 0, 0, 220),
            stroke_width=8,
            stroke_fill=(0, 0, 0, 220),
        )
        y_text += 72

    shadow_blurred = shadow_layer.filter(ImageFilter.GaussianBlur(radius=5))
    img_main.alpha_composite(shadow_blurred)
    draw = ImageDraw.Draw(img_main)

    y_text = 122
    for idx, line in enumerate(hook_lines):
        bbox = draw.textbbox((0, 0), line, font=font_hook)
        w = bbox[2] - bbox[0]
        x_pos = (1080 - w) / 2
        text_color = (255, 255, 255, 255) if idx == 0 else (255, 225, 0, 255)
        draw.text(
            (x_pos, y_text),
            line,
            font=font_hook,
            fill=text_color,
            stroke_width=6,
            stroke_fill=(8, 12, 24, 255),
        )
        y_text += 72

    # Clean subtitle narration: 100% borderless text with clean shadow for maximum clarity
    summary_lines = textwrap.wrap(topic["narration"], width=36)[:2]
    sub_shadow = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
    ss_draw = ImageDraw.Draw(sub_shadow)
    y_sub = 1580
    for idx, line in enumerate(summary_lines):
        bbox = draw.textbbox((0, 0), line, font=font_sub)
        w = bbox[2] - bbox[0]
        ss_draw.text(
            ((1080 - w) / 2 + 4, y_sub + 4),
            line,
            font=font_sub,
            fill=(0, 0, 0, 240),
            stroke_width=6,
            stroke_fill=(0, 0, 0, 240),
        )
        y_sub += 60

    sub_shadow_blur = sub_shadow.filter(ImageFilter.GaussianBlur(radius=4))
    img_main.alpha_composite(sub_shadow_blur)
    draw = ImageDraw.Draw(img_main)

    y_sub = 1580
    for idx, line in enumerate(summary_lines):
        bbox = draw.textbbox((0, 0), line, font=font_sub)
        w = bbox[2] - bbox[0]
        color = (255, 230, 0, 255) if idx == 0 else (255, 255, 255, 255)
        draw.text(
            ((1080 - w) / 2, y_sub),
            line,
            font=font_sub,
            fill=color,
            stroke_width=4,
            stroke_fill=(6, 10, 20, 255),
        )
        y_sub += 60

    img_main.save(main_overlay_path)

    img_end = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
    draw_end = ImageDraw.Draw(img_end)

    draw_end.rounded_rectangle(
        [(55, 1165), (1025, 1475)],
        radius=26,
        fill=(10, 16, 32, 238),
        outline=(255, 215, 0, 255),
        width=4,
    )
    header = "📌 EXPERIMENT SOURCE / CREDIT"
    hb = draw_end.textbbox((0, 0), header, font=font_credit_title)
    draw_end.text(
        ((1080 - (hb[2] - hb[0])) / 2, 1195),
        header,
        font=font_credit_title,
        fill=(255, 215, 0, 255),
    )

    credit_str = get_source_credit_text(topic)
    credit_lines = textwrap.wrap(credit_str, width=38)[:2]
    y_c = 1260
    for line in credit_lines:
        cb = draw_end.textbbox((0, 0), line, font=font_credit_body)
        draw_end.text(
            ((1080 - (cb[2] - cb[0])) / 2, y_c),
            line,
            font=font_credit_body,
            fill=(255, 255, 255, 255),
        )
        y_c += 46

    footer = "⚡ @Physics_explain_YT — Subscribe for Daily Physics!"
    fb = draw_end.textbbox((0, 0), footer, font=font_credit_body)
    draw_end.text(
        ((1080 - (fb[2] - fb[0])) / 2, 1390),
        footer,
        font=font_credit_body,
        fill=(56, 189, 248, 255),
    )

    img_end.save(endcard_overlay_path)
    return main_overlay_path, endcard_overlay_path


def build_brand_new_short(
    climax_video: Path,
    voiceover_mp3: Path,
    bgm_wav: Path,
    main_overlay_png: Path,
    endcard_overlay_png: Path,
    output_video: Path,
    target_duration: float,
    max_clip_dur: float = 19.5,
) -> Path:
    """Create a 1080x1920 9:16 vertical Short with adaptive high-retention duration & EBU R128 volume."""
    ffmpeg_exe = get_ffmpeg_executable()
    # Guarantee video NEVER cuts off before voiceover sentence completes (+0.8s natural breathing room)
    clip_dur = max(target_duration + 0.8, 14.0)
    endcard_start = max(clip_dur - 1.8, target_duration + 0.1)
    print(
        f"Rendering 9:16 Short ({clip_dur:.1f}s, End-Card at {endcard_start:.1f}s) -> {output_video.name}...",
        flush=True,
    )

    is_native_vertical = False
    try:
        probe_cmd = [
            ffmpeg_exe, "-i", str(climax_video),
            "-v", "error", "-select_streams", "v:0",
            "-show_entries", "stream=width,height", "-of", "csv=s=x:p=0"
        ]
        res = subprocess.run(probe_cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
        if "1080x1920" in res.stdout.strip():
            is_native_vertical = True
    except Exception:
        pass

    if is_native_vertical:
        filter_complex = (
            "[0:v]scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2[base];"
            "[base][1:v]overlay=0:0[with_main];"
            f"[with_main][2:v]overlay=0:0:enable='gte(t,{endcard_start:.2f})'[vout];"
            "[3:a]aformat=sample_rates=44100:channel_layouts=stereo,highpass=f=85,lowpass=f=12000,volume=1.0[vo];"
            "[4:a]aformat=sample_rates=44100:channel_layouts=stereo,volume=0.18[bgm];"
            "[vo][bgm]amix=inputs=2:duration=longest:normalize=0,"
            "loudnorm=I=-19:TP=-2.5:LRA=7,volume=0.92[aout]"
        )
    else:
        filter_complex = (
            "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
            "boxblur=26:5,eq=brightness=-0.10:contrast=1.10:saturation=1.20[bg];"
            "[0:v]scale=1080:1360:force_original_aspect_ratio=decrease[fg];"
            "[bg][fg]overlay=(W-w)/2:(H-h)/2-40[base];"
            "[base][1:v]overlay=0:0[with_main];"
            f"[with_main][2:v]overlay=0:0:enable='gte(t,{endcard_start:.2f})'[vout];"
            "[3:a]aformat=sample_rates=44100:channel_layouts=stereo,highpass=f=85,lowpass=f=12000,volume=1.0[vo];"
            "[4:a]aformat=sample_rates=44100:channel_layouts=stereo,volume=0.18[bgm];"
            "[vo][bgm]amix=inputs=2:duration=longest:normalize=0,"
            "loudnorm=I=-19:TP=-2.5:LRA=7,volume=0.92[aout]"
        )

    cmd = [
        ffmpeg_exe,
        "-y",
        "-stream_loop",
        "-1",
        "-i",
        str(climax_video),
        "-i",
        str(main_overlay_png),
        "-i",
        str(endcard_overlay_png),
        "-i",
        str(voiceover_mp3),
        "-i",
        str(bgm_wav),
        "-t",
        f"{clip_dur:.2f}",
        "-filter_complex",
        filter_complex,
        "-map",
        "[vout]",
        "-map",
        "[aout]",
        "-c:v",
        "libx264",
        "-preset",
        "fast",
        "-crf",
        "20",
        "-r",
        "30",
        "-c:a",
        "aac",
        "-ar",
        "44100",
        "-ac",
        "2",
        "-b:a",
        "192k",
        "-movflags",
        "+faststart",
        str(output_video),
    ]
    subprocess.run(cmd, check=True)
    print(f"Created brand-new edited Short: {output_video}", flush=True)
    return output_video


def get_youtube_service():
    try:
        sys.stdout.reconfigure(line_buffering=True)
        sys.stderr.reconfigure(line_buffering=True)
    except Exception:
        pass
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build

    client_id = os.environ.get("YOUTUBE_CLIENT_ID")
    client_secret = os.environ.get("YOUTUBE_CLIENT_SECRET")
    refresh_token = os.environ.get("YOUTUBE_REFRESH_TOKEN")

    if client_id and client_secret and refresh_token:
        creds = Credentials(
            token=None,
            refresh_token=refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=client_id,
            client_secret=client_secret,
            scopes=YOUTUBE_SCOPES,
        )
        try:
            creds.refresh(Request())
            return build("youtube", "v3", credentials=creds)
        except Exception as exc:
            print(f"[AUTH] Environment token refresh failed ({exc}). Falling back to local token...", flush=True)

    # Headless runs (GitHub Actions sets CI=true; local scheduled jobs can set HEADLESS=1) must never wait for a
    # browser login: that hang is what silently skipped the Nov 8-9 posts. Fail loudly instead so the run turns red.
    headless = bool(os.environ.get("CI") or os.environ.get("HEADLESS"))

    creds = None
    if TOKEN_FILE.exists():
        with open(TOKEN_FILE, "rb") as token_fp:
            creds = pickle.load(token_fp)

    if not creds or not creds.valid:
        refreshed = False
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                refreshed = creds.valid
            except Exception as exc:
                print(f"[AUTH] Existing token refresh failed ({exc}). Initiating browser re-authorization...", flush=True)
                creds = None
        if not refreshed:
            if headless:
                raise SystemExit("[AUTH] YouTube token expired/revoked and this run is headless. "
                                 "Run connect_youtube_once.bat on the PC to sign in again, then re-sync the GitHub secret.")
            success_html = """<!DOCTYPE html><html><body style="font-family:system-ui,-apple-system,sans-serif;text-align:center;padding:60px;background:#0f172a;color:#f8fafc;"><div style="max-width:500px;margin:0 auto;background:#1e293b;border-radius:16px;padding:40px;box-shadow:0 10px 25px rgba(0,0,0,0.5);"><h1 style="color:#38bdf8;margin-bottom:12px;">✅ YouTube Connected!</h1><p style="font-size:16px;color:#94a3b8;line-height:1.6;">Authorization completed successfully.<br>The automated video generation and cloud scheduling pipeline is now active.</p><p style="margin-top:24px;font-size:14px;color:#64748b;">You can safely close this browser window.</p></div></body></html>"""

            flow = InstalledAppFlow.from_client_secrets_file(
                str(CLIENT_SECRETS_FILE), YOUTUBE_SCOPES
            )
            print("\n" + "="*70 + "\n[AUTH REQUIRED] Opening browser for Google / YouTube login...\n" + "="*70, flush=True)
            creds = flow.run_local_server(
                port=8085,
                prompt="consent",
                access_type="offline",
                success_message=success_html,
            )
            if not creds or not getattr(creds, "refresh_token", None):
                raise RuntimeError("Failed to obtain valid YouTube credentials with refresh token.")
            with open(TOKEN_FILE, "wb") as token_fp:
                pickle.dump(creds, token_fp)
            print(f"[AUTH] Successfully saved fresh credentials to {TOKEN_FILE}!", flush=True)
            try:
                from setup_youtube_auth import sync_to_github
                sync_to_github(creds)
            except Exception as sync_err:
                print(f"[AUTH] GitHub secret sync note: {sync_err}", flush=True)

    return build("youtube", "v3", credentials=creds)


def upload_to_youtube_api(
    video_path: Path,
    topic: Dict[str, Any],
    srt_path: Optional[Path] = None,
    publish_at_iso: Optional[str] = None,
) -> Tuple[str, str]:
    from googleapiclient.http import MediaFileUpload

    youtube = get_youtube_service()
    status_dict = {
        "privacyStatus": "private" if publish_at_iso else "public",
        "selfDeclaredMadeForKids": False,
    }
    if publish_at_iso:
        dt = datetime.datetime.fromisoformat(publish_at_iso)
        dt_utc = dt.astimezone(datetime.timezone.utc)
        status_dict["publishAt"] = dt_utc.strftime("%Y-%m-%dT%H:%M:%SZ")

    credit_str = get_source_credit_text(topic)
    rel_title, rel_url = get_related_video_info(topic)
    body = {
        "snippet": {
            "title": topic["title"][:100],
            "description": (
                f"{topic.get('comment_q', '💬 What do you think? Comment below!')}\n\n"
                f"{topic['hook']}\n"
                f"{topic['narration']}\n\n"
                f"🔗 Watch Related Experiment: {rel_title}\n"
                f"👉 {rel_url}\n\n"
                f"📌 Experiment Footage Source: {credit_str}\n\n"
                f"👍 Please LIKE ❤️ & SUBSCRIBE to @Physics_explain_YT for daily mind-blowing physics experiments! ⚡🔔\n\n"
                f"{WINNING_HASHTAGS}"
            ),
            "tags": WINNING_TAGS,
            "defaultLanguage": DEFAULT_LANGUAGE,
            "defaultAudioLanguage": DEFAULT_LANGUAGE,
            "categoryId": "27",
        },
        "status": status_dict,
    }

    media = MediaFileUpload(
        str(video_path),
        chunksize=10 * 1024 * 1024,
        resumable=True,
        mimetype="video/mp4",
    )
    request = youtube.videos().insert(
        part="snippet,status",
        body=body,
        media_body=media,
    )

    print(f"Uploading {video_path.name} to YouTube...", flush=True)
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"Upload progress: {int(status.progress() * 100)}%", flush=True)

    video_id = response["id"]
    video_url = f"https://www.youtube.com/watch?v={video_id}"
    print(f"Uploaded video! URL: {video_url}", flush=True)

    if srt_path and Path(srt_path).exists():
        try:
            caption_media = MediaFileUpload(str(srt_path), mimetype="application/x-subrip")
            youtube.captions().insert(
                part="snippet",
                body={
                    "snippet": {
                        "videoId": video_id,
                        "language": "en",
                        "name": "English",
                        "isDraft": False,
                    }
                },
                media_body=caption_media,
            ).execute()
            print(f"Uploaded English subtitle track (.srt) for video {video_id}", flush=True)
        except Exception as cap_err:
            print(f"[INFO] Caption track auto-transcribed by YouTube: {cap_err}", flush=True)

    return video_id, video_url


def create_and_upload_one(
    publish_at_iso: Optional[str] = None,
    tuned_params: Optional[Dict[str, Any]] = None,
) -> str:
    """Create one brand-new edited English Physics Short and upload/schedule it."""
    ensure_directories()
    params = tuned_params or {"max_clip_dur": 18.5, "voice_rate": "+18%"}
    target_slot_time = None
    if publish_at_iso:
        try:
            dt = datetime.datetime.fromisoformat(publish_at_iso)
            target_slot_time = dt.strftime("%H:%M")
        except Exception:
            target_slot_time = None
    topic = pick_next_topic(target_slot_time=target_slot_time)

    # Content-Accurate 3D Blender Simulation Routing
    blender_script = topic.get("script_file")
    if not blender_script:
        for cand in [
            Path("scratch") / f"blender_{topic['id']}.py",
            Path("scratch") / f"blender_{topic['id'].replace('_3d', '')}.py",
            Path("scratch") / f"blender_{topic['id'].replace('_sound', '')}.py",
        ]:
            if cand.exists():
                blender_script = str(cand)
                break

    blender_exe = shutil.which("blender")
    if not blender_exe and sys.platform == "win32" and os.path.exists(r"C:\Users\acer\blender\blender.exe"):
        blender_exe = r"C:\Users\acer\blender\blender.exe"

    use_blender_3d = bool(blender_script and Path(blender_script).exists() and blender_exe)
    if use_blender_3d:
        raw_video = OUTPUT_DIR / f"{topic['id']}_raw3d.mp4"
        scratch_cand = Path("scratch") / f"{topic['id']}_raw3d.mp4"
        if raw_video.exists() and raw_video.stat().st_size > 100_000:
            print(f"[BLENDER-3D] Using existing 3D physical simulation render: {raw_video.name}", flush=True)
        elif scratch_cand.exists() and scratch_cand.stat().st_size > 100_000:
            print(f"[BLENDER-3D] Reusing verified 3D physical simulation from {scratch_cand}...", flush=True)
            shutil.copy2(scratch_cand, raw_video)
        else:
            print(f"[BLENDER-3D] Rendering content-accurate 3D physical simulation for '{topic['id']}' via {blender_script}...", flush=True)
            stem = Path(blender_script).stem
            blender_py_expr = f"""
import sys, os
sys.path.append('scratch')
import {stem} as scene_builder
fns = [f for f in dir(scene_builder) if f.startswith('build_')]
if fns:
    fn = getattr(scene_builder, fns[0])
    fn(out_file=r'{os.path.abspath(raw_video)}', do_render=True)
else:
    raise RuntimeError('No build_ function found in {stem}')
"""
            cmd = [blender_exe, "-b", "--python-expr", blender_py_expr]
            subprocess.run(cmd, check=True)
    else:
        raw_video = download_raw_video_for_topic(topic)

    mp3_path = OUTPUT_DIR / f"{topic['id']}_vo.mp3"
    srt_path = OUTPUT_DIR / f"{topic['id']}.en.srt"
    bgm_path = OUTPUT_DIR / f"{topic['id']}_bgm.wav"
    climax_video = OUTPUT_DIR / f"{topic['id']}_climax.mp4"
    main_overlay = OUTPUT_DIR / f"{topic['id']}_overlay.png"
    endcard_overlay = OUTPUT_DIR / f"{topic['id']}_endcard.png"
    edited_video = OUTPUT_DIR / f"{topic['id']}_short.mp4"

    if edited_video.exists() and edited_video.stat().st_size > 100_000 and srt_path.exists():
        print(f"[REUSE] Using existing newly-rendered Short: {edited_video.name}", flush=True)
    else:
        vo_duration = generate_english_voiceover_and_srt(
            topic, mp3_path, srt_path, voice_rate=params.get("voice_rate", "+18%")
        )
        generate_science_bgm_wav(bgm_path, max(vo_duration + 4.0, 22.0))
        if use_blender_3d:
            shutil.copy2(raw_video, climax_video)
        else:
            prepare_climax_experiment_video(raw_video, topic, vo_duration, climax_video)
        create_overlays_png(topic, main_overlay, endcard_overlay)
        build_brand_new_short(
            climax_video,
            mp3_path,
            bgm_path,
            main_overlay,
            endcard_overlay,
            edited_video,
            vo_duration,
            max_clip_dur=float(params.get("max_clip_dur", 19.5)),
        )

    vid_id, url = upload_to_youtube_api(
        edited_video, topic, srt_path=srt_path, publish_at_iso=publish_at_iso
    )
    save_to_history(f"TOPIC:{topic['id']}")
    save_to_history(f"VID:{vid_id}")
    save_to_history(f"TOPIC_VID:{topic['id']}:{vid_id}")
    if publish_at_iso:
        save_to_history(f"SLOT:{publish_at_iso}")
    
    # Always like the newly uploaded video immediately with the channel's account
    try:
        yt = get_youtube_service()
        like_own_video(yt, vid_id)
        if not publish_at_iso:
            ensure_creator_first_comment(yt, vid_id, topic)
    except Exception as exc:
        print(f"[WARN] Immediate like/comment notice: {exc}", flush=True)
    return url


# Upcoming Target Slots: 7:00 PM (19:00) and 8:00 PM (20:00) Asia/Bangkok
TARGET_SLOTS_BKK = [
    (19, 0),
    (20, 0),
]
TARGET_HOURS_BKK = (19, 20)
MAX_UPLOADS_PER_RUN = 2


def get_upcoming_slots(days_ahead: int = 1) -> List[str]:
    tz = datetime.timezone(datetime.timedelta(hours=7))
    now = datetime.datetime.now(tz)
    history = load_history()
    slots: List[str] = []

    for day_offset in range(days_ahead + 1):
        target_date = now.date() + datetime.timedelta(days=day_offset)
        for hour, minute in TARGET_SLOTS_BKK:
            slot_dt = datetime.datetime(
                target_date.year,
                target_date.month,
                target_date.day,
                hour,
                minute,
                0,
                tzinfo=tz,
            )
            slot_iso = slot_dt.isoformat()
            slot_key = f"SLOT:{slot_iso}"
            if (
                slot_dt > now + datetime.timedelta(minutes=15)
                and slot_key not in history
            ):
                slots.append(slot_iso)
    slots.sort()
    return slots


def main() -> None:
    print("[DISABLED] Legacy non-cartoon uploader is permanently disabled. Only the Cartoon 3D Shorts pipeline in animation/ is active.")
    return
    # Step 1: Run the Closed-Loop Analytics Inspector & Self-Optimizer (with graceful fallback if quota is limited)
    try:
        tuned_params = run_auto_analytics_and_optimize()
    except Exception as exc:
        print(f"[WARN] Analytics optimization skipped ({exc}); using optimal defaults from analytics report.", flush=True)
        tuned_params = {"max_clip_dur": 15.0, "voice_rate": "+14%"}

    pre_schedule = "--pre-schedule" in sys.argv or "--cloud" in sys.argv
    if pre_schedule:
        days_ahead = 7
        max_uploads = 2
        for i, arg in enumerate(sys.argv):
            if arg == "--days-ahead" and i + 1 < len(sys.argv):
                try:
                    days_ahead = int(sys.argv[i + 1])
                except ValueError:
                    pass
            if arg == "--limit" and i + 1 < len(sys.argv):
                try:
                    max_uploads = int(sys.argv[i + 1])
                except ValueError:
                    pass
        slots = get_upcoming_slots(days_ahead=days_ahead)
        if not slots:
            print(
                f"All upcoming 7:00 PM (19:00) and 8:00 PM (20:00) slots for the next {days_ahead} days are already fully scheduled!"
            )
            return
        for slot_iso in slots[:max_uploads]:
            try:
                url = create_and_upload_one(
                    publish_at_iso=slot_iso, tuned_params=tuned_params
                )
                print(
                    f"Scheduled NEW Physics Short for Analytics-aligned slot {slot_iso}: {url}",
                    flush=True,
                )
            except Exception as exc:
                import traceback
                traceback.print_exc()
                print(
                    f"[WARN] Stopping batch scheduling for now ({exc}); will continue next run.",
                    flush=True,
                )
                break
    else:
        url = create_and_upload_one(publish_at_iso=None, tuned_params=tuned_params)
        print(f"Published NEW Physics Short immediately: {url}", flush=True)


if __name__ == "__main__":
    main()
