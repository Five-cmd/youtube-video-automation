"""Cartoon-short posting helper for the cloud workflow.

usage:
  python animation/post_queue.py next            -> prints the next approved, unposted comp id (empty if none)
  python animation/post_queue.py upload <comp>   -> uploads animation/out/final.mp4 for <comp> and marks it posted

Only entries with approved=true are ever uploaded. Uses YOUTUBE_CLIENT_ID / _SECRET / _REFRESH_TOKEN from the env.
Never opens a browser: an invalid token fails the run (red X on GitHub) instead of hanging.
"""
import json
import os
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
QUEUE = HERE / "queue.json"
SCOPES = ["https://www.googleapis.com/auth/youtube.upload", "https://www.googleapis.com/auth/youtube.force-ssl"]


def load():
    return json.loads(QUEUE.read_text(encoding="utf-8"))


def save(q):
    QUEUE.write_text(json.dumps(q, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def next_comp():
    for s in load()["shorts"]:
        if s.get("approved") and not s.get("posted"):
            return s["comp"]
    return ""


def comp_frames(comp: str) -> int:
    if comp == "BridgeShort":
        m = re.search(r"export const TOTAL\s*=\s*(\d+)", (HERE / "src/videos/bridge/story.ts").read_text(encoding="utf-8"))
        if m:
            return int(m.group(1))
        return 2025
    slug = comp.replace("Short", "").lower()
    txt = (HERE / "src/videos/physics/PhysicsShort.tsx").read_text(encoding="utf-8")
    m = re.search(rf"{slug}\s*:\s*(\d+)", txt)
    if m:
        return int(m.group(1))
    raise SystemExit(f"Unknown frame count for {comp}")


def description(slug: str) -> str:
    md = (HERE / "shorts" / slug / "SCRIPT.md").read_text(encoding="utf-8")
    script_sec = md.split("## Script", 1)[-1].split("\n## ", 1)[0]
    script = "\n".join(script_sec.splitlines()[1:]).strip()
    facts = md.split("## Facts", 1)[-1].split("\n## ", 1)[0]
    sources = sorted(set(re.findall(r"\(([^()]*(?:Wikipedia|archives|calculation|electromagnetism)[^()]*)\)", facts)))
    src = "\n".join(f"- {s}" for s in sources[:6])
    return f"{script}\n\nSources:\n{src}\n\n#physics #science #shorts #history"


def youtube():
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build

    creds = Credentials(None, refresh_token=os.environ["YOUTUBE_REFRESH_TOKEN"], token_uri="https://oauth2.googleapis.com/token",
                        client_id=os.environ["YOUTUBE_CLIENT_ID"], client_secret=os.environ["YOUTUBE_CLIENT_SECRET"], scopes=SCOPES)
    creds.refresh(Request())  # raises on invalid_grant -> run fails loudly
    return build("youtube", "v3", credentials=creds)


def upload(comp: str, video: Path):
    from googleapiclient.http import MediaFileUpload

    q = load()
    entry = next(s for s in q["shorts"] if s["comp"] == comp)
    if not entry.get("approved"):
        raise SystemExit(f"{comp} is not approved; refusing to upload")
    if entry.get("posted"):
        raise SystemExit(f"{comp} already posted ({entry.get('video_id')})")
    body = {
        "snippet": {"title": entry["title"][:100], "description": description(entry["slug"]), "categoryId": "27",
                    "tags": ["physics", "science", "history", "animation", "shorts"], "defaultLanguage": "en", "defaultAudioLanguage": "en"},
        "status": {"privacyStatus": "public", "selfDeclaredMadeForKids": False},
    }
    req = youtube().videos().insert(part="snippet,status", body=body,
                                    media_body=MediaFileUpload(str(video), chunksize=8 * 1024 * 1024, resumable=True, mimetype="video/mp4"))
    resp = None
    while resp is None:
        _, resp = req.next_chunk()
    entry["posted"], entry["video_id"] = True, resp["id"]
    save(q)
    print(f"UPLOADED {comp}: https://youtube.com/shorts/{resp['id']}")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "next"
    if cmd == "next":
        print(next_comp())
    elif cmd == "frames":
        print(comp_frames(sys.argv[2]))
    elif cmd == "upload":
        upload(sys.argv[2], HERE / "out" / "final.mp4")
