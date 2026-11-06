import os
import sys
import math
import random
import asyncio
import subprocess
import json
import glob
import pickle
from pathlib import Path
import edge_tts
import imageio_ffmpeg
import numpy as np

def run_blender_render():
    print("[1/4] Running Blender 3D Cable Zoom render on Cloud Runner...", flush=True)
    blender_bin = "blender"
    if sys.platform == "win32":
        local_blender = r"C:\Users\acer\blender\blender.exe"
        if os.path.exists(local_blender):
            blender_bin = local_blender

    # Run blender script
    script_path = "scratch/blender_cable_zoom_acdc.py"
    cmd = [blender_bin, "-b", "-P", script_path]
    subprocess.run(cmd, check=True)
    
    # Locate output
    out_candidates = glob.glob("scratch/blender_cable_zoom_1080x1920*.mp4")
    if not out_candidates:
        raise FileNotFoundError("Blender output not found!")
    raw_mp4 = out_candidates[0]
    print(f"[BLENDER OK] Generated raw 3D video: {raw_mp4} ({os.path.getsize(raw_mp4):,} bytes)", flush=True)
    return raw_mp4

async def gen_vo(text: str, out_path: str):
    comm = edge_tts.Communicate(text, "en-US-ChristopherNeural", rate="+10%", pitch="-2Hz")
    await comm.save(out_path)
    print(f"[VO OK] Saved narration: {out_path}", flush=True)

def format_ass_time(sec: float) -> str:
    h = int(sec // 3600)
    m = int((sec % 3600) // 60)
    s = int(sec % 60)
    cs = int(round((sec - int(sec)) * 100))
    if cs >= 100:
        cs = 99
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"

def get_word_timestamps(audio_path: str):
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    cmd = [ff, "-y", "-i", audio_path, "-f", "f32le", "-ac", "1", "-ar", "16000", "-"]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, check=True)
    audio_data = np.frombuffer(res.stdout, dtype=np.float32)

    from faster_whisper import WhisperModel
    model = WhisperModel("base", device="cpu", compute_type="int8")
    segments, _ = model.transcribe(audio_data, word_timestamps=True)
    
    words = []
    for s in segments:
        for w in s.words:
            clean_word = w.word.strip()
            if clean_word:
                words.append({
                    "word": clean_word,
                    "start": float(w.start),
                    "end": float(w.end)
                })
    return words

EMPHASIS_WORDS = {
    "NEVER", "WRONG", "SHOOT", "SPEED", "LIGHT", "DRIFT", "VIBRATE",
    "FOCUSED", "FREEZES", "SHOCK", "EXPLODES", "TOUCH", "MILLION", "VOLTS",
    "INVISIBLE", "WAVE", "THIN", "AIR", "ZERO", "DESTROY", "POWER"
}

def build_ass(words, ass_path: str):
    chunks = []
    cur_chunk = []
    for w in words:
        cur_chunk.append(w)
        if len(cur_chunk) >= 3 or cur_chunk[-1]["word"].endswith((".", "!", "?", ",")):
            chunks.append(cur_chunk)
            cur_chunk = []
    if cur_chunk:
        chunks.append(cur_chunk)

    ass_lines = [
        "[Script Info]",
        "ScriptType: v4.00+",
        "PlayResX: 1080",
        "PlayResY: 1920",
        "",
        "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
        "Style: ZackD,Arial Black,78,&H00FFFFFF,&H000000FF,&H00000000,&H80000000,1,0,0,0,100,100,2,0,1,8,2,2,60,60,420,1",
        "",
        "[Events]",
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"
    ]

    for chunk in chunks:
        start_t = chunk[0]["start"]
        end_t = chunk[-1]["end"]
        text_parts = []
        for item in chunk:
            raw = item["word"].upper()
            clean = raw.strip(".,!?\"'")
            if clean in EMPHASIS_WORDS or any(k in clean for k in ["WRONG", "NEVER", "SHOCK"]):
                text_parts.append(f"{{\\c&H0000FFFF&}}{raw}{{\\c&H00FFFFFF&}}")
            else:
                text_parts.append(raw)
        chunk_text = " ".join(text_parts)
        ass_lines.append(
            f"Dialogue: 0,{format_ass_time(start_t)},{format_ass_time(end_t)},ZackD,,0,0,0,,{chunk_text}"
        )

    with open(ass_path, "w", encoding="utf-8") as f:
        f.write("\n".join(ass_lines))
    print(f"[ASS OK] Created subtitles -> {ass_path}", flush=True)

def composite_short(raw_video: str, vo_mp3: str, ass_path: str, bgm_wav: str, out_mp4: str):
    print("[2/4] Compositing video with Zack D style pop captions & audio...", flush=True)
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    ass_rel = ass_path.replace(os.sep, "/")

    filter_complex = (
        f"[0:v]subtitles={ass_rel}[vout];"
        f"[1:a]aformat=sample_rates=44100:channel_layouts=stereo,highpass=f=80,lowpass=f=12000,volume=1.05[vo];"
        f"[2:a]aformat=sample_rates=44100:channel_layouts=stereo,volume=0.18[bgm];"
        f"[vo][bgm]amix=inputs=2:duration=first:normalize=0,"
        f"loudnorm=I=-17:TP=-1.5:LRA=7,volume=0.95[aout]"
    )

    cmd = [
        ff, "-y",
        "-i", raw_video,
        "-i", vo_mp3,
        "-stream_loop", "-1", "-i", bgm_wav,
        "-filter_complex", filter_complex,
        "-map", "[vout]",
        "-map", "[aout]",
        "-c:v", "libx264",
        "-preset", "slow",
        "-crf", "16",
        "-r", "24",
        "-c:a", "aac",
        "-b:a", "256k",
        "-movflags", "+faststart",
        out_mp4
    ]
    subprocess.run(cmd, check=True)
    print(f"[COMPOSITE OK] Finished Short: {out_mp4} ({os.path.getsize(out_mp4):,} bytes)", flush=True)

def upload_and_replace_b1M(final_mp4: str):
    print("[3/4] Uploading to YouTube and replacing b1M5vSLzWkc...", flush=True)
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload
    from google.oauth2.credentials import Credentials

    # Handle both Cloud environment variables and local pickle
    creds = None
    if os.environ.get("YOUTUBE_CLIENT_ID") and os.environ.get("YOUTUBE_REFRESH_TOKEN"):
        creds = Credentials(
            token=None,
            refresh_token=os.environ.get("YOUTUBE_REFRESH_TOKEN"),
            token_uri="https://oauth2.googleapis.com/token",
            client_id=os.environ.get("YOUTUBE_CLIENT_ID"),
            client_secret=os.environ.get("YOUTUBE_CLIENT_SECRET"),
        )
    elif os.path.exists("youtube_token.pickle"):
        with open("youtube_token.pickle", "rb") as f:
            creds = pickle.load(f)

    yt = build("youtube", "v3", credentials=creds)

    title = "AC vs DC: What REALLY Happens Inside Wire?! ⚡ (Zack D. 3D Zoom) #shorts #physics #science"
    description = (
        "You might think electrons inside your household wire shoot forward at the speed of light. But that is completely WRONG!\n\n"
        "In direct current (DC), electrons slowly drift forward at just a fraction of a millimeter per second.\n\n"
        "And in alternating current (AC), electrons NEVER actually leave your wall! They furiously vibrate back and forth 60 times a second, transferring pure electromagnetic energy straight to your devices at light speed!\n\n"
        "💬 Did you know AC electrons only vibrate in place? Drop your thoughts below!\n\n"
        "🔔 Subscribe to @Physics_explain_YT for daily 3D physics simulations & mind-blowing science experiments!\n\n"
        "#shorts #physics #science #stem #3danimation #blender #electricity #zackdfilms"
    )

    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": ["physics", "science", "blender", "3d animation", "ac dc", "electricity", "zack d films", "shorts", "stem"],
            "categoryId": "28"
        },
        "status": {
            "privacyStatus": "private",
            "publishAt": "2026-11-08T17:30:00Z", # Keep original slot time of b1M5vSLzWkc!
            "selfDeclaredMadeForKids": False
        }
    }

    media = MediaFileUpload(final_mp4, mimetype="video/mp4", resumable=True)
    req = yt.videos().insert(part="snippet,status", body=body, media_body=media)
    res = req.execute()
    new_vid_id = res["id"]
    print(f"[YOUTUBE OK] Uploaded new HQ 3D Zoom video: {new_vid_id}", flush=True)

    # Like new video
    try:
        yt.videos().rate(id=new_vid_id, rating="like").execute()
        print(f"[LIKE OK] Liked {new_vid_id}!", flush=True)
    except Exception as e:
        print(f"[LIKE WARN] {e}", flush=True)

    # Delete old b1M5vSLzWkc
    try:
        yt.videos().delete(id="b1M5vSLzWkc").execute()
        print(f"[DELETE OK] Successfully deleted old low-quality b1M5vSLzWkc!", flush=True)
    except Exception as e:
        print(f"[DELETE WARN] {e}", flush=True)

    # Update uploaded_history.json
    try:
        with open("uploaded_history.json", "r", encoding="utf-8") as f:
            h = json.load(f)
        h["processed"].append(f"VID:{new_vid_id}")
        h["processed"].append(f"LIKED_OWN_VIDEO:{new_vid_id}")
        h["processed"].append(f"TOPIC_VID:ac_dc_electron_drift_3d:{new_vid_id}")
        with open("uploaded_history.json", "w", encoding="utf-8") as f:
            json.dump(h, f, indent=2)
    except Exception as e:
        print(f"[HISTORY WARN] {e}", flush=True)

    return new_vid_id

def main():
    script_text = (
        "You might think electrons inside your household wire shoot forward at the speed of light. "
        "But that is completely WRONG! "
        "In direct current, electrons drift forward at just a fraction of a millimeter per second. "
        "And in alternating current, electrons NEVER actually leave your wall! "
        "They just furiously vibrate back and forth sixty times a second, "
        "transferring pure electromagnetic energy straight to your devices at light speed!"
    )
    vo_path = "scratch/cable_zoom_vo.mp3"
    ass_path = "scratch/cable_zoom_subtitles.ass"
    bgm_path = "scratch/driving_synth_bgm.wav"
    out_mp4 = "output/acdc_cable_zoom_zack_d_b1M.mp4"
    os.makedirs("output", exist_ok=True)
    os.makedirs("scratch", exist_ok=True)

    # 1. Run Blender
    raw_video = run_blender_render()

    # 2. Audio & Captions
    asyncio.run(gen_vo(script_text, vo_path))
    words = get_word_timestamps(vo_path)
    build_ass(words, ass_path)

    # 3. Composite
    composite_short(raw_video, vo_path, ass_path, bgm_path, out_mp4)

    # 4. Upload & Replace
    new_id = upload_and_replace_b1M(out_mp4)
    print(f"\n[ALL DONE] Replaced b1M5vSLzWkc with new 3D Zoom Short: https://youtube.com/shorts/{new_id}", flush=True)

if __name__ == "__main__":
    main()
