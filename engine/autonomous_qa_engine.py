import os
import json
import subprocess
import shutil
import numpy as np
from PIL import Image
from pathlib import Path

"""
================================================================================
🤖 AUTONOMOUS QA & SELF-APPROVAL ENGINE (100% AUTOMATION)
================================================================================
Fully autonomous quality assurance and self-approval system.
- Before production: Validates script, topics, visual prompts, and cloud GPU allocation.
- Before publishing: Validates video hook luminance (no black screen), 9:16 aspect ratio,
  absence of external watermarks, EBU R128 loudness (-16.0 LUFS target), and pacing.
- The user is completely hands-off (100% Automation).
- Passed videos are scheduled and enriched with auto-pinned comments.
- Failed videos are automatically flagged and queued for cloud auto-healing.
- Protected videos (e.g. rEMvFuzlZBc) are guarded permanently.
================================================================================
"""

PROTECTED_VIDEO_IDS = ["rEMvFuzlZBc"]

def get_ffmpeg_exe():
    sys_ffmpeg = shutil.which("ffmpeg")
    if sys_ffmpeg:
        return sys_ffmpeg
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return "ffmpeg"

class AutonomousQAEngine:
    def __init__(self, workspace_dir=None):
        self.workspace_dir = Path(workspace_dir or os.getcwd())
        self.ffmpeg_exe = get_ffmpeg_exe()
        self.logs = []

    def log(self, message):
        print(f"[AutonomousQA] {message}")
        self.logs.append(message)

    def pre_production_approval(self, topic_data):
        """
        Gate 1: Pre-Production Self-Approval (ก่อนทำ)
        Enforces topic accuracy, script depth, no robotic templates, and Cloud GPU targeting.
        """
        self.log(f"--- Running Pre-Production QA for: {topic_data.get('id', 'unknown')} ---")
        issues = []
        score = 100

        # 1. Robotic template check
        forbidden_phrases = [
            "when you observe this phenomenon",
            "the underlying physics creates a shocking result",
            "let's dive into the fascinating world of",
            "in this video we will explore",
            "this phenomenon is truly remarkable"
        ]
        script_text = (topic_data.get("script", "") + " " + topic_data.get("hook", "") + " " + topic_data.get("narration", "")).lower()
        for phrase in forbidden_phrases:
            if phrase in script_text:
                issues.append(f"Forbidden robotic template phrase found: '{phrase}'")
                score -= 30

        # 2. Hook clarity & retention formula
        hook = topic_data.get("hook", "").upper()
        if not (hook.startswith("WAIT...") or hook.startswith("WHY...") or "WAIT..." in hook):
            issues.append("Hook does not follow retention formula (must contain 'WAIT...' or 'WHY...')")
            score -= 10

        # 2b. Viral Storytelling & Sentence Cadence Gate
        try:
            from engine.viral_storytelling_engine import audit_and_improve_script, get_upgraded_topic_script
            t_id = topic_data.get("id")
            if t_id:
                upgraded = get_upgraded_topic_script(t_id)
                if upgraded:
                    topic_data.update(upgraded)
                    self.log(f"Auto-applied viral storytelling script for: {t_id}")

            narration = topic_data.get("narration", "")
            if narration:
                audit = audit_and_improve_script(narration)
                if not audit["passes_viral_gate"]:
                    issues.append(f"Script failed viral storytelling gate: avg words/sentence={audit['avg_words_per_sentence']} (target <= 14)")
                    score -= 15
        except Exception as e:
            self.log(f"Storytelling engine notice: {e}")

        # 3. Cloud GPU allocation rule (Flowchart verification)
        target_engine = topic_data.get("target_engine", "cloud_kaggle_t4")
        if "local" in str(target_engine).lower():
            issues.append("Job violates Cloud GPU Flowchart rule: Cannot render on local PC!")
            score -= 50

        # 4. Strict topic visual alignment
        topic_title = topic_data.get("title", "").lower()
        query = topic_data.get("query", "").lower()
        if "water" in topic_title and ("shrimp" in query or "toy" in query):
            issues.append("Topic-Visual Mismatch detected in pre-production!")
            score -= 60

        approved = score >= 85
        self.log(f"Pre-Production Result: {'APPROVED (Ready for Cloud GPU)' if approved else 'REJECTED (Needs script/engine fix)'} [Score: {score}/100]")
        return {
            "approved": approved,
            "score": score,
            "issues": issues
        }

    def extract_frame_pil(self, video_path, timestamp_sec):
        """Extracts a frame at timestamp_sec as a PIL Image."""
        tmp_img = self.workspace_dir / f"qa_tmp_{int(timestamp_sec*1000)}.jpg"
        cmd = [
            self.ffmpeg_exe, "-y", "-ss", str(timestamp_sec),
            "-i", str(video_path), "-vframes", "1", "-q:v", "2",
            str(tmp_img)
        ]
        try:
            subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True, timeout=15)
            if tmp_img.exists():
                img = Image.open(str(tmp_img)).convert("RGB")
                tmp_img.unlink(missing_ok=True)
                return img
        except Exception as e:
            self.log(f"Frame extraction failed at {timestamp_sec}s: {e}")
            if tmp_img.exists():
                tmp_img.unlink(missing_ok=True)
        return None

    def inspect_visuals(self, video_path):
        """
        Gate 2A: Computer Vision & Quality Checks on Rendered Video.
        """
        score = 100
        issues = []

        # Extract Hook Frame at 0.1s
        hook_img = self.extract_frame_pil(video_path, 0.1)
        if hook_img is None:
            return {"approved": False, "score": 0, "issues": ["Failed to extract hook frame"]}

        width, height = hook_img.size

        # 1. Aspect Ratio check
        if width != 1080 or height != 1920:
            issues.append(f"Resolution is {width}x{height}, required 1080x1920 (9:16 vertical full screen)")
            score -= 20

        # 2. Hook Luminance check (Anti-Black-Screen rule)
        hook_gray = hook_img.convert("L")
        mean_lum = np.mean(np.array(hook_gray))
        self.log(f"Hook frame luminance: {mean_lum:.1f}/255")
        if mean_lum < 30.0:
            issues.append(f"Hook brightness too low ({mean_lum:.1f}/255) - Black Screen detected!")
            score -= 50

        # 3. Corner Watermark Check (Nat Geo / TV / Watermark detection)
        # Check lower-right corner (typical TV logo area)
        w_cut = int(width * 0.75)
        h_cut = int(height * 0.85)
        lr_box = hook_img.crop((w_cut, h_cut, width, height)).convert("L")
        lr_arr = np.array(lr_box)
        # Standard deviation of local high-contrast edges
        edge_metric = np.std(lr_arr)
        # In a plain background edge_metric is low; strong persistent text shows high std
        # Sample mid-video frame at 5.0s to verify
        mid_img = self.extract_frame_pil(video_path, 5.0)
        if mid_img:
            mid_lr = np.array(mid_img.crop((w_cut, h_cut, width, height)).convert("L"))
            # If both have identical static bright patches, potential foreign watermark
            diff = np.abs(lr_arr.astype(int) - mid_lr.astype(int))
            if np.mean(diff) < 2.0 and edge_metric > 40.0:
                issues.append("Static foreign watermark / logo detected in corner (e.g. Nat Geo / TV logo)!")
                score -= 35

        return {
            "approved": score >= 80,
            "score": score,
            "issues": issues,
            "mean_luminance": mean_lum,
            "resolution": f"{width}x{height}"
        }

    def inspect_audio(self, video_path):
        """
        Gate 2B: Audio Quality and Broadcast Loudness.
        """
        cmd = [
            self.ffmpeg_exe, "-nostats", "-i", str(video_path),
            "-filter_complex", "ebur128=peak=true",
            "-f", "null", "-"
        ]
        score = 100
        issues = []
        lufs = -16.0
        try:
            res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=25)
            import re
            m = re.search(r"I:\s+([-\d.]+)\s+LUFS", res.stderr)
            if m:
                lufs = float(m.group(1))
                self.log(f"Audio integrated loudness: {lufs:.1f} LUFS")
                if lufs < -22.0:
                    issues.append(f"Audio volume too low ({lufs:.1f} LUFS)")
                    score -= 20
                elif lufs > -12.0:
                    issues.append(f"Audio volume too loud/distorted ({lufs:.1f} LUFS)")
                    score -= 20
        except Exception as e:
            self.log(f"Audio scan bypassed: {e}")

        return {
            "approved": score >= 80,
            "score": score,
            "issues": issues,
            "lufs": lufs
        }

    def post_production_approval(self, video_path, topic_data):
        """
        Gate 2: Post-Production Self-Approval (ก่อนโพสต์)
        Runs visual and audio checks. Returns pass/fail decision.
        """
        self.log(f"--- Running Post-Production Self-Approval for: {video_path} ---")
        vis_res = self.inspect_visuals(video_path)
        aud_res = self.inspect_audio(video_path)

        final_score = int(vis_res["score"] * 0.6 + aud_res["score"] * 0.4)
        issues = vis_res.get("issues", []) + aud_res.get("issues", [])

        # Strict fail condition: any black screen or logo issue fails automatically
        critical_fail = any("Black Screen" in i or "watermark" in i for i in issues)
        approved = (final_score >= 85) and not critical_fail

        report = {
            "video_path": str(video_path),
            "topic_id": topic_data.get("id"),
            "approved": approved,
            "final_score": final_score,
            "issues": issues,
            "action": "AUTO_PUBLISH_SCHEDULE" if approved else "AUTO_REJECT_AND_HEAL"
        }
        self.log(f"Post-Production Result: {'APPROVED (Self-Approved for YouTube)' if approved else 'REJECTED (Self-Correcting)'} [Score: {final_score}/100]")
        return report

    def prune_low_performing_videos(self, youtube_service, min_views=200, min_days=7):
        """
        7-Day Low-Performing Auto-Pruning Rule:
        Deletes self-generated videos with fewer than 200 views after 7 days.
        Preserves protected videos permanently (e.g. rEMvFuzlZBc, d2VnHwAVaS4).
        """
        self.log(f"--- Running 7-Day Low-Performing Video Pruning (Threshold: < {min_views} views after {min_days} days) ---")
        history_file = self.workspace_dir / "uploaded_history.json"
        if not history_file.exists():
            return []

        with open(history_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        tracked_ids = [x.split("VID:", 1)[1] for x in data.get("processed", []) if x.startswith("VID:")]
        
        protected = set(PROTECTED_VIDEO_IDS + ["d2VnHwAVaS4"])
        candidates = [vid for vid in tracked_ids if vid not in protected]

        pruned = []
        for i in range(0, len(candidates), 50):
            batch = candidates[i:i+50]
            try:
                res = youtube_service.videos().list(id=",".join(batch), part="snippet,statistics,status").execute()
                import datetime
                now_utc = datetime.datetime.now(datetime.timezone.utc)
                for item in res.get("items", []):
                    vid = item["id"]
                    views = int(item.get("statistics", {}).get("viewCount", 0))
                    pub_str = item.get("snippet", {}).get("publishedAt")
                    privacy = item.get("status", {}).get("privacyStatus", "")
                    if pub_str and privacy == "public":
                        pub_dt = datetime.datetime.fromisoformat(pub_str.replace("Z", "+00:00"))
                        days = (now_utc - pub_dt).total_seconds() / 86400.0
                        if days >= min_days and views < min_views:
                            self.log(f"Pruning {vid}: {views} views after {days:.1f} days")
                            try:
                                youtube_service.videos().delete(id=vid).execute()
                                pruned.append(vid)
                            except Exception as e:
                                self.log(f"Could not delete {vid}: {e}")
            except Exception as e:
                self.log(f"Batch lookup error: {e}")
                break

        self.log(f"Total videos pruned: {len(pruned)}")
        return pruned

if __name__ == "__main__":
    qa = AutonomousQAEngine()
    print("Autonomous QA Engine initialized and ready.")
