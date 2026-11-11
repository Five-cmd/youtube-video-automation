"""Legacy YouTube helper module (RETIRED).

NOTE: The legacy non-animation FFmpeg/HUD video pipeline has been permanently retired by the user.
All YouTube Shorts are now rendered and uploaded exclusively by the Cartoon 3D Physics Shorts
pipeline in `animation/` via GitHub Actions (`.github/workflows/daily_youtube_upload.yml`)
at 4 clips per day (04:00->06:00, 07:00->09:00, 19:00->21:00, 21:00->23:00 Asia/Bangkok).

DO NOT restore legacy non-animation video generation or uploading here.
"""
import os
import pickle
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

BASE_DIR = Path(__file__).resolve().parent
CLIENT_SECRETS_FILE = BASE_DIR / "client_secrets.json"
TOKEN_FILE = BASE_DIR / "youtube_token.pickle"
YOUTUBE_SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.force-ssl",
]
MAX_UPLOADS_PER_RUN = 0


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
                print(f"[AUTH] Existing token refresh failed ({exc}).", flush=True)
                creds = None
        if not refreshed:
            if headless:
                raise SystemExit("[AUTH] YouTube token expired/revoked and this run is headless.")
            flow = InstalledAppFlow.from_client_secrets_file(
                str(CLIENT_SECRETS_FILE), YOUTUBE_SCOPES
            )
            creds = flow.run_local_server(port=8085, prompt="consent", access_type="offline")
            with open(TOKEN_FILE, "wb") as token_fp:
                pickle.dump(creds, token_fp)

    return build("youtube", "v3", credentials=creds)


def run_auto_analytics_and_optimize() -> Dict[str, Any]:
    raise RuntimeError("Legacy non-animation pipeline is permanently retired. Use animation/post_queue.py via GitHub Actions.")


def upload_to_youtube_api(*args: Any, **kwargs: Any) -> Tuple[str, str]:
    raise RuntimeError("Legacy non-animation pipeline is permanently retired. Use animation/post_queue.py via GitHub Actions.")


def create_and_upload_one(*args: Any, **kwargs: Any) -> str:
    raise RuntimeError("Legacy non-animation pipeline is permanently retired. Use animation/post_queue.py via GitHub Actions.")


def get_upcoming_slots(days_ahead: int = 1) -> List[str]:
    return []


def main() -> None:
    print("[RETIRED] Legacy non-animation pipeline is permanently retired. Cartoon 3D Physics Shorts run via GitHub Actions (.github/workflows/daily_youtube_upload.yml).")


if __name__ == "__main__":
    main()
