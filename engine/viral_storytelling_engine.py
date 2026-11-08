"""
================================================================================
🎬 VIRAL STORYTELLING & VISUAL COMMUNICATION ENGINE
================================================================================
Inspired by Zack D. Films, Veritasium, MinutePhysics, and Kurzgesagt.
Guarantees high viewer retention, intuitive communication, punchy sentences,
and content-accurate 3D animation choreography across all video productions.
================================================================================
"""

from typing import Dict, Any, List
import re

STORYTELLING_RULES = {
    "hook": {
        "max_duration_sec": 3.0,
        "max_words": 15,
        "principles": [
            "Disrupt everyday intuition immediately.",
            "Violate common sense expectations with high visual stakes.",
            "Never start with academic definitions, background history, or setup instructions."
        ]
    },
    "sentences": {
        "max_words_per_beat": 13,
        "active_verbs": ["blast", "freeze", "crush", "snap", "trap", "defy", "slam", "leap", "ignite", "drag", "squeeze", "spin", "tear"],
        "forbidden_phrases": [
            "is defined as", "the phenomenon known as", "in this video we will",
            "turn up ultrasonic speakers to", "it is important to note", "due to the fact that",
            "wrap a thick copper coil around", "discharge a bank of"
        ]
    },
    "animation_choreography": {
        "phase_1_hook": "Macro camera establishing shot with dramatic cinematic lighting.",
        "phase_2_push": "Dynamic camera push-in / X-ray cutaway directly into the invisible physics zone.",
        "phase_3_forces": "Color-coded force fields (Cyan = Acoustic/Electric wave, Amber = Pressure/Mass, Crimson = Friction/Resistance).",
        "phase_4_payoff": "Visible physical consequence (squash-and-stretch liquid deformation, harmonic resonance, instant levitation)."
    }
}

VIRAL_UPGRADED_SCRIPTS: Dict[str, Dict[str, Any]] = {
    "acoustic_levitation_3d": {
        "title": "Can SOUND Defy Gravity and Levitate Water?! 🔊💧 (3D Science) #shorts #physics",
        "hook": "WAIT... SOUND WAVES CAN PICK UP OBJECTS?!",
        "narration": (
            "If you blast sound at a droplet of water... it doesn't splash. It freezes in mid-air! "
            "Between two ultrasonic speakers, high-frequency sound waves rush at each other and collide. "
            "Their peaks cancel out, carving invisible pockets of zero pressure called acoustic nodes. "
            "These pockets act like invisible sonic hands, clamping the droplet from both sides "
            "and locking it motionless against gravity!"
        ),
        "comment_q": "💬 Scientists now use this to levitate human cells in space. What would you try levitating?",
        "animation_cues": [
            {"time": "0.0s - 3.0s", "shot": "Macro close-up of water droplet dropping between dark metal transducers."},
            {"time": "3.0s - 8.0s", "shot": "Camera plunges in: Translucent cyan 40kHz sound waves collide into a standing wave."},
            {"time": "8.0s - 14.0s", "shot": "Color-coded pressure heatmaps show high-pressure cushions forming above and below."},
            {"time": "14.0s - 19.0s", "shot": "Droplet squashes slightly from radiation pressure, hovering in perfect stable equilibrium."}
        ]
    },
    "electromagnetic_pinch_3d": {
        "title": "50,000 Amperes vs. Soda Can in 3D! ⚡🥤 #shorts #physics",
        "hook": "WAIT... INVISIBLE MAGNETISM CAN CRUSH METAL?!",
        "narration": (
            "What happens when you blast fifty thousand amps of electricity through a soda can? "
            "It doesn't melt. It violently pinches in half! "
            "When capacitors dump high voltage into a copper coil, an insane magnetic wave slams into the aluminum. "
            "This wave forces opposing currents to fight each other. "
            "Opposite currents violently repel, creating tons of inward magnetic pressure. "
            "In less than a millisecond, the invisible force crushes the metal like paper!"
        ),
        "comment_q": "💬 Would a steel can crush faster or survive the magnetic pinch? Comment your guess!",
        "animation_cues": [
            {"time": "0.0s - 3.0s", "shot": "Soda can sitting inside copper coil, sparks ignite on switch."},
            {"time": "3.0s - 7.5s", "shot": "Dynamic camera zoom: Pulsing magnetic field lines wrap around the can."},
            {"time": "7.5s - 13.0s", "shot": "Cyan opposing eddy currents fight amber primary coil currents."},
            {"time": "13.0s - 18.0s", "shot": "Colossal inward Lorentz force clamps the aluminum waist into an hourglass pinch."}
        ]
    },
    "voltage_current_cutaway_3d": {
        "title": "Voltage vs Current: What ACTUALLY Happens Inside The Wire! ⚡ #shorts #physics",
        "hook": "WAIT... ELECTRICITY ISN'T WHAT YOU THINK?!",
        "narration": (
            "You use electricity every day, but do you know what's actually inside the wire? "
            "Think of electrons like water rushing through a pipe. "
            "CURRENT is simply how many electrons pass through every second. "
            "VOLTAGE isn't the electricity itself—it's the massive push shoving them forward! "
            "And RESISTANCE is the clamp trying to choke the pipe. "
            "Voltage pushes, resistance chokes, and current is what survives to power your world!"
        ),
        "comment_q": "💬 What is your favorite way to picture Ohm's Law? Tell us below!",
        "animation_cues": [
            {"time": "0.0s - 3.5s", "shot": "Cross-section cutaway slicing through an ordinary household copper wire."},
            {"time": "3.5s - 9.0s", "shot": "Amber electron spheres drifting, with blue pressure gradient illustrating voltage push."},
            {"time": "9.0s - 15.0s", "shot": "Mechanical clamp choking the pipe representing resistance heat and collision."},
            {"time": "15.0s - 20.0s", "shot": "Final balanced current flowing out to light up a glowing filament."}
        ]
    },
    "triboluminescence_sparks_3d": {
        "title": "Why Crushing Sugar In The Dark Sparks BLUE LIGHT! 🍬✨ #shorts #physics",
        "hook": "WAIT... CRUSHING CANDY MAKES ELECTRIC LIGHT?!",
        "narration": (
            "If you crush plain sugar in total darkness... it flashes with bright blue sparks! "
            "There are no batteries inside, so where is this glowing light coming from? "
            "When mechanical force snaps the crystal lattice, chemical bonds rip apart unevenly. "
            "This creates millions of volts of static charge across the microscopic crack. "
            "Electrons jump the gap, smashing into nitrogen molecules in the air and lighting up the room! "
            "This is Triboluminescence!"
        ),
        "comment_q": "💬 Have you ever seen Wint-O-Green Life Savers spark in the dark? Comment below!",
        "animation_cues": [
            {"time": "0.0s - 3.0s", "shot": "Pliers crushing a crystalline sugar cube in pitch blackness, sudden blue flash."},
            {"time": "3.0s - 8.5s", "shot": "Ultra slow-motion zoom into atomic crystal lattice shearing apart."},
            {"time": "8.5s - 14.0s", "shot": "Positive and negative charge separation creating glowing electric field lines."},
            {"time": "14.0s - 19.5s", "shot": "Electron avalanche exciting ambient nitrogen gas into ultraviolet/blue photon bursts."}
        ]
    },
    "crookes_radiometer_3d": {
        "title": "Why Does Light SPIN This Glass Engine in a Vacuum?! 💡 #shorts #physics",
        "hook": "WAIT... LIGHT CAN PHYSICALLY PUSH AND SPIN AN ENGINE?!",
        "narration": (
            "Inside this sealed glass vacuum bulb sits a rotor with four vanes. "
            "Shine a flashlight on it... and it starts spinning at crazy speeds! "
            "Each vane is silver on one side and black on the other. "
            "The black side absorbs light and heats up, while the silver side stays cool. "
            "Residual gas molecules bounce off the hotter black side with much more kinetic force, "
            "kick-starting an invisible heat engine that spins the rotor!"
        ),
        "comment_q": "💬 Would it spin faster or completely stop in an absolute perfect vacuum? Comment your guess!",
        "animation_cues": [
            {"time": "0.0s - 3.5s", "shot": "Sealed glass bulb with stationary 4-vane rotor, flashlight clicks on, rapid spin starts."},
            {"time": "3.5s - 9.0s", "shot": "Microscopic view of silver vs black vane face with thermal heat color map."},
            {"time": "9.0s - 15.0s", "shot": "Gas molecules ricocheting with high thermal kinetic impulse off black vane edge."},
            {"time": "15.0s - 20.0s", "shot": "Thermal creep force driving the continuous frictionless rotation."}
        ]
    },
    "three_phase_ac_rotating_field_3d": {
        "title": "Three-Phase AC: How Motors Spin With ZERO Contact in 3D! ⚡ #shorts #physics",
        "hook": "WAIT... MOTORS SPIN WITH ZERO TOUCHING PARTS?!",
        "narration": (
            "How do giant industrial motors spin at thousands of RPM with zero touching parts? "
            "Ordinary motors grind carbon brushes against spinning copper. "
            "They wear down and throw sparks. "
            "Three-phase motors use three coils firing in sequence, one hundred twenty degrees apart. "
            "Their magnetic fields combine into an invisible, rotating magnetic tornado! "
            "This spinning vortex drags the solid metal rotor along with it, creating massive torque straight from thin air!"
        ),
        "comment_q": "💬 Did you know Tesla invented the three-phase AC motor? Drop your thoughts below!",
        "animation_cues": [
            {"time": "0.0s - 3.0s", "shot": "Industrial motor cutaway showing rotor hovering inside 3 stator coils."},
            {"time": "3.0s - 8.0s", "shot": "Color-coded 3-phase currents (Red, Green, Blue) pulsing in 120-degree wave sequence."},
            {"time": "8.0s - 14.0s", "shot": "Composite magnetic vector arrow rotating smoothly in 3D circle."},
            {"time": "14.0s - 19.0s", "shot": "Rotor locking onto the magnetic vortex and spinning at high speed with zero friction."}
        ]
    },
    "lenz_law_copper_tube": {
        "title": "Why Did This Magnet FREEZE Inside Copper?! ⚡ #shorts #physics",
        "hook": "WAIT... WHY DID THIS MAGNET FREEZE IN MID-AIR?!",
        "narration": (
            "Drop a heavy neodymium magnet through a copper pipe... and gravity suddenly loses! "
            "Copper isn't even magnetic. "
            "So why does the magnet slow down to a crawl? "
            "As the magnet falls, its moving magnetic field forces electrons inside the copper into spinning whirlpools called eddy currents. "
            "These whirlpools create their own opposing magnetic cushion. "
            "The cushion pushes upward against the falling magnet, locking it in a slow-motion levitation brake!"
        ),
        "comment_q": "💬 What happens if you drop it through an aluminum pipe instead? Drop your guess below!",
        "animation_cues": [
            {"time": "0.0s - 3.0s", "shot": "Neodymium magnet dropped into top of vertical copper pipe, camera peers down the bore."},
            {"time": "3.0s - 8.0s", "shot": "X-ray cutaway: Magnet slowly descending like it's submerged in thick honey."},
            {"time": "8.0s - 14.0s", "shot": "Glowing cyan eddy current loops swirl around the pipe wall."},
            {"time": "14.0s - 19.0s", "shot": "Upward magnetic flux vectors balancing gravitational downward force."}
        ]
    },
    "prince_ruperts_drop": {
        "title": "Bullet vs. UNBREAKABLE Glass Drop in 3D! 💥 #shorts #physics",
        "hook": "WAIT... A GLASS DROP SHATTERS A SPEEDING BULLET?!",
        "narration": (
            "Watch what happens when a speeding bullet slams directly into this glass drop. "
            "The glass doesn't break. The bullet completely shatters! "
            "When molten glass drips into ice-cold water, the outer skin freezes instantly. "
            "Meanwhile, the hot molten core contracts inward, creating insane compressive stress of twenty-five thousand PSI! "
            "The bulbous head can survive bullets and hydraulic presses. "
            "But snip the tiny tail... and the entire drop violently detonates into dust!"
        ),
        "comment_q": "💬 Would a diamond hydraulic press crush the head first? Comment below!",
        "animation_cues": [
            {"time": "0.0s - 3.5s", "shot": "Slow-motion bullet impacting the head of Prince Rupert's drop, bullet disintegrating."},
            {"time": "3.5s - 9.0s", "shot": "Cross-section thermal stress map showing dark blue exterior compression shell and red core tension."},
            {"time": "9.0s - 14.0s", "shot": "Crack propagation through tail traveling at Mach 5 (over 1 mile per second)."},
            {"time": "14.0s - 19.0s", "shot": "Explosive catastrophic decompression turning the entire drop into microscopic glass mist."}
        ]
    }
}


def audit_and_improve_script(script_text: str) -> Dict[str, Any]:
    """Audits any narration against viral storytelling & communication principles."""
    words = script_text.split()
    total_words = len(words)
    sentences = [s.strip() for s in re.split(r'[.!?]+', script_text) if s.strip()]

    # Check average sentence length
    avg_words = total_words / max(len(sentences), 1)

    # Check for passive or academic buzzwords
    flagged_fluff = []
    for phrase in STORYTELLING_RULES["sentences"]["forbidden_phrases"]:
        if phrase in script_text.lower():
            flagged_fluff.append(phrase)

    # Check active verb punchiness
    active_hits = [v for v in STORYTELLING_RULES["sentences"]["active_verbs"] if v in script_text.lower()]

    score = 100
    if avg_words > 14:
        score -= 15
    if flagged_fluff:
        score -= 20 * len(flagged_fluff)
    if len(active_hits) < 2:
        score -= 15

    return {
        "score": max(0, score),
        "total_words": total_words,
        "sentence_count": len(sentences),
        "avg_words_per_sentence": round(avg_words, 1),
        "flagged_academic_fluff": flagged_fluff,
        "active_action_verbs": active_hits,
        "passes_viral_gate": score >= 75
    }


def get_upgraded_topic_script(topic_id: str) -> Dict[str, Any]:
    """Returns the upgraded viral script for a given topic ID if available."""
    return VIRAL_UPGRADED_SCRIPTS.get(topic_id)
