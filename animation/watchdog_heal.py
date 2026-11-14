"""Autonomous Watchdog for Cartoon 3D Shorts pipeline.

Syncs YouTube uploads into animation/queue.json, inspects GitHub Actions
check-run annotations and failed job logs, applies safe automatic fixes
(e.g. missing Python dependencies in requirements-audio.txt, publish-only
reruns, hung run cancellation), and files a deduplicated GitHub Issue for
non-auto-fixable code errors.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import requests
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

PYPI_IMPORT_MAP = {
    "cv2": "opencv-python",
    "PIL": "Pillow",
    "yaml": "PyYAML",
    "edge_tts": "edge-tts",
    "imageio_ffmpeg": "imageio-ffmpeg",
    "googleapiclient": "google-api-python-client",
}

CODE_ERROR_PATTERNS = (
    "AttributeError:",
    "TypeError:",
    "SyntaxError:",
    "NameError:",
    "ReferenceError:",
)


def gh_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"}


def git_commit_and_push(paths: list[str], message: str) -> None:
    subprocess.run(["git", "config", "user.name", "github-actions[bot]"], check=True)
    subprocess.run(
        ["git", "config", "user.email", "github-actions[bot]@users.noreply.github.com"],
        check=True,
    )
    subprocess.run(["git", "add", *paths], check=True)
    diff = subprocess.run(["git", "diff", "--cached", "--quiet"])
    if diff.returncode == 0:
        return
    subprocess.run(["git", "commit", "-m", message], check=True)
    subprocess.run(["git", "pull", "--rebase", "--autostash"], check=True)
    subprocess.run(["git", "push"], check=True)


def sync_youtube_queue(queue_path: Path) -> dict:
    with queue_path.open("r", encoding="utf-8") as f:
        q = json.load(f)

    try:
        creds = Credentials(
            None,
            refresh_token=os.environ.get("YOUTUBE_REFRESH_TOKEN"),
            token_uri="https://oauth2.googleapis.com/token",
            client_id=os.environ.get("YOUTUBE_CLIENT_ID"),
            client_secret=os.environ.get("YOUTUBE_CLIENT_SECRET"),
        )
        creds.refresh(Request())
        yt = build("youtube", "v3", credentials=creds)
        ch = yt.channels().list(part="contentDetails", mine=True).execute()
        up_id = ch["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
        pl = yt.playlistItems().list(part="snippet", playlistId=up_id, maxResults=25).execute()
        yt_titles = {
            it["snippet"]["title"]: it["snippet"]["resourceId"]["videoId"]
            for it in pl.get("items", [])
        }
        changed = False
        for s in q.get("shorts", []):
            if not s.get("posted") and s["title"] in yt_titles:
                s["posted"] = True
                s["video_id"] = yt_titles[s["title"]]
                changed = True
                print(f"Watchdog: Synced '{s['comp']}' ({s['video_id']}) into queue.json")
        if changed:
            queue_path.write_text(
                json.dumps(q, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
            )
            git_commit_and_push([str(queue_path)], "watchdog: sync posted video_id from YouTube")
    except Exception as exc:
        print(f"Watchdog: YouTube sync warning (continuing): {exc}")

    return q


def fetch_annotations_and_logs(
    owner: str, repo: str, jobs: list[dict], headers: dict[str, str]
) -> tuple[list[dict], list[tuple[str, str]]]:
    annotations: list[dict] = []
    failed_logs: list[tuple[str, str]] = []

    for job in jobs:
        jid = job["id"]
        ann_url = f"https://api.github.com/repos/{owner}/{repo}/check-runs/{jid}/annotations?per_page=50"
        resp = requests.get(ann_url, headers=headers, timeout=20)
        if resp.status_code == 200:
            for ann in resp.json():
                ann["job_name"] = job["name"]
                annotations.append(ann)

        if job.get("conclusion") == "failure":
            log_url = f"https://api.github.com/repos/{owner}/{repo}/actions/jobs/{jid}/logs"
            lresp = requests.get(log_url, headers=headers, timeout=30)
            if lresp.status_code == 200:
                tail = "\n".join(lresp.text.splitlines()[-80:])
                failed_logs.append((job["name"], tail))

    return annotations, failed_logs


def write_step_summary(
    run_id: int, status: str, conclusion: str | None, annotations: list[dict], actions_taken: list[str]
) -> None:
    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if not summary_path:
        return
    lines = [
        f"## Watchdog Report (Run `{run_id}`)",
        f"- **Status**: `{status}` | **Conclusion**: `{conclusion}`",
        f"- **Annotations found**: `{len(annotations)}`",
        "",
    ]
    if annotations:
        lines.append("### Annotations")
        for ann in annotations[:20]:
            lvl = ann.get("annotation_level", "notice")
            jname = ann.get("job_name", "?")
            msg = ann.get("message", "").replace("\n", " ")[:240]
            lines.append(f"- **[{lvl}]** `{jname}`: {msg}")
        lines.append("")
    if actions_taken:
        lines.append("### Actions Taken")
        for act in actions_taken:
            lines.append(f"- {act}")
    with open(summary_path, "a", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def try_fix_missing_python_module(failed_logs: list[tuple[str, str]]) -> str | None:
    req_path = Path("animation/requirements-audio.txt")
    if not req_path.exists():
        return None
    existing = {line.strip().lower() for line in req_path.read_text(encoding="utf-8").splitlines() if line.strip()}
    for _, log_text in failed_logs:
        m = re.search(r"ModuleNotFoundError: No module named ['\"]([A-Za-z0-9_.-]+)['\"]", log_text)
        if not m:
            continue
        mod = m.group(1).split(".")[0]
        pkg = PYPI_IMPORT_MAP.get(mod, mod)
        if pkg.lower() in existing:
            continue
        content = req_path.read_text(encoding="utf-8").rstrip() + f"\n{pkg}\n"
        req_path.write_text(content, encoding="utf-8")
        git_commit_and_push([str(req_path)], f"watchdog: add missing dependency '{pkg}' to requirements-audio.txt")
        return pkg
    return None


def find_code_error(annotations: list[dict], failed_logs: list[tuple[str, str]]) -> str | None:
    for ann in annotations:
        if ann.get("annotation_level") == "failure":
            msg = ann.get("message", "")
            if any(p in msg for p in CODE_ERROR_PATTERNS):
                return f"{ann.get('job_name')}: {msg[:400]}"
    for jname, log_text in failed_logs:
        for pat in CODE_ERROR_PATTERNS:
            if pat in log_text:
                excerpt = "\n".join(log_text.splitlines()[-25:])
                return f"Job `{jname}` failed with `{pat}`:\n```\n{excerpt}\n```"
    return None


def open_or_update_issue(
    owner: str, repo: str, headers: dict[str, str], comp: str, run_id: int, detail: str
) -> None:
    title = f"[Watchdog] Auto-Heal Alert: {comp}"
    issues_url = f"https://api.github.com/repos/{owner}/{repo}/issues?state=open&per_page=20"
    resp = requests.get(issues_url, headers=headers, timeout=20)
    if resp.status_code != 200:
        print(f"Watchdog: Could not list issues ({resp.status_code})")
        return
    existing = next((it for it in resp.json() if it["title"] == title), None)
    body = (
        f"Watchdog detected a non-auto-fixable code error on run `{run_id}` for `{comp}`.\n\n"
        f"{detail}\n\n"
        f"Run link: https://github.com/{owner}/{repo}/actions/runs/{run_id}"
    )
    if existing:
        c_url = f"https://api.github.com/repos/{owner}/{repo}/issues/{existing['number']}/comments"
        requests.post(c_url, headers=headers, json={"body": body}, timeout=20)
        print(f"Watchdog: Updated issue #{existing['number']}")
    else:
        requests.post(
            f"https://api.github.com/repos/{owner}/{repo}/issues",
            headers=headers,
            json={"title": title, "body": body},
            timeout=20,
        )
        print("Watchdog: Created new alert issue")


def main() -> int:
    gh_token = os.environ["GH_TOKEN"]
    owner = os.environ["OWNER"]
    repo = os.environ["REPO"]
    headers = gh_headers(gh_token)
    actions_taken: list[str] = []

    q = sync_youtube_queue(Path("animation/queue.json"))
    unposted = [s for s in q.get("shorts", []) if s.get("approved") and not s.get("posted")]
    if not unposted:
        print("Watchdog: All approved shorts are already posted. Nothing pending.")
        return 0

    target = unposted[0]
    print(f"Watchdog: Target unposted short is '{target['comp']}' ({target['title']})")

    wf_url = f"https://api.github.com/repos/{owner}/{repo}/actions/workflows/daily_youtube_upload.yml/runs?per_page=5"
    r = requests.get(wf_url, headers=headers, timeout=20)
    if r.status_code != 200:
        print(f"Failed to fetch runs: {r.status_code}")
        return 1

    runs = r.json().get("workflow_runs", [])
    disp_url = f"https://api.github.com/repos/{owner}/{repo}/actions/workflows/daily_youtube_upload.yml/dispatches"
    if not runs:
        disp = requests.post(disp_url, headers=headers, json={"ref": "main"}, timeout=20)
        print(f"No runs found. Dispatched new run: {disp.status_code}")
        return 0

    for r in runs[:5]:
        rs = r.get("status")
        r_age = (datetime.now(timezone.utc) - datetime.fromisoformat(r["created_at"].replace("Z", "+00:00"))).total_seconds() / 60
        if rs in ("queued", "pending", "waiting") or (rs == "in_progress" and r_age < 75):
            print(f"Run {r['id']} is already active/waiting ({rs}, {r_age:.1f}m). Watchdog standing by.")
            return 0

    latest = runs[0]
    status = latest.get("status")
    conclusion = latest.get("conclusion")
    run_id = latest["id"]
    created_at = datetime.fromisoformat(latest["created_at"].replace("Z", "+00:00"))
    age_min = (datetime.now(timezone.utc) - created_at).total_seconds() / 60

    print(f"Latest run {run_id}: status={status}, conclusion={conclusion}, age={age_min:.1f} mins")

    if status == "in_progress" and age_min >= 75:
        print(f"Run {run_id} hung ({age_min:.1f}m). Cancelling...")
        requests.post(f"https://api.github.com/repos/{owner}/{repo}/actions/runs/{run_id}/cancel", headers=headers, timeout=20)
        actions_taken.append(f"Cancelled hung run `{run_id}` ({age_min:.1f}m)")

    jobs = requests.get(
        f"https://api.github.com/repos/{owner}/{repo}/actions/runs/{run_id}/jobs?per_page=30",
        headers=headers,
        timeout=20,
    ).json().get("jobs", [])

    annotations, failed_logs = fetch_annotations_and_logs(owner, repo, jobs, headers)
    print(f"Watchdog: Read {len(annotations)} annotation(s) and {len(failed_logs)} failed job log(s).")
    for ann in annotations:
        print(f"  Annotation [{ann.get('annotation_level')}] {ann.get('job_name')}: {ann.get('message', '')[:180]}")

    # 1. Auto-fix missing Python package if detected in logs
    added_pkg = try_fix_missing_python_module(failed_logs)
    if added_pkg:
        actions_taken.append(f"Added missing Python package `{added_pkg}` to `animation/requirements-audio.txt` and pushed to `main`")
        disp = requests.post(disp_url, headers=headers, json={"ref": "main"}, timeout=20)
        actions_taken.append(f"Dispatched fresh run after dependency fix (`{disp.status_code}`)")
        write_step_summary(run_id, status, conclusion, annotations, actions_taken)
        return 0

    # 2. Rerun only publish job if all renders + audio succeeded
    pub_failed = any(j["name"] == "publish" and j["conclusion"] == "failure" for j in jobs)
    render_ok = all(j["conclusion"] == "success" for j in jobs if j["name"].startswith("render"))
    audio_ok = any(j["name"] == "audio" and j["conclusion"] == "success" for j in jobs)
    if pub_failed and render_ok and audio_ok and age_min < 240:
        rf = requests.post(
            f"https://api.github.com/repos/{owner}/{repo}/actions/runs/{run_id}/rerun-failed-jobs",
            headers=headers,
            timeout=20,
        )
        actions_taken.append(f"All renders+audio ok; reran failed `publish` job (`{rf.status_code}`)")
        write_step_summary(run_id, status, conclusion, annotations, actions_taken)
        if rf.status_code == 201:
            return 0

    # 3. If a non-auto-fixable code bug is detected, open/update a GitHub Issue & avoid tight loop
    code_err = find_code_error(annotations, failed_logs)
    if code_err:
        open_or_update_issue(owner, repo, headers, target["comp"], run_id, code_err)
        actions_taken.append("Opened/updated GitHub Issue with exact annotation/traceback; skipped blind retry")
        write_step_summary(run_id, status, conclusion, annotations, actions_taken)
        return 0

    # 4. Avoid tight loop on 3 consecutive failures within 30 mins
    recent_fails = [
        x for x in runs[:3]
        if x.get("conclusion") == "failure"
        and (datetime.now(timezone.utc) - datetime.fromisoformat(x["created_at"].replace("Z", "+00:00"))).total_seconds() < 1800
    ]
    if len(recent_fails) >= 3 and os.environ.get("GITHUB_EVENT_NAME") == "workflow_run":
        actions_taken.append("3 consecutive failures within 30m — waiting for next scheduled check")
        write_step_summary(run_id, status, conclusion, annotations, actions_taken)
        return 0

    disp = requests.post(disp_url, headers=headers, json={"ref": "main"}, timeout=20)
    actions_taken.append(f"Dispatched fresh run (`{disp.status_code}`)")
    write_step_summary(run_id, status, conclusion, annotations, actions_taken)
    return 0


if __name__ == "__main__":
    sys.exit(main())
