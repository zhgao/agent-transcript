"""Fetch public YouTube comments for a video with yt-dlp (no keys, $0).

Usage:
    python comment_fetch.py <video_url_or_id> [--max-comments N]
        [--out comments.json] [--yt-dlp PATH]

Writes one JSON object: {"video_id", "title", "channel", "comment_count",
"fetched_at", "comments": [{"index","text","like_count","parent"}]}.

Notes for this sandbox (2026-11-07, verified):
- yt-dlp is NOT installed by default; `pip install yt-dlp` into the venv.
- The sandbox egress proxy MITMs TLS. yt-dlp defaults to certifi's CA
  bundle, which does NOT contain the Hatch CA, so plain yt-dlp fails with
  "SSL: CERTIFICATE_VERIFY_FAILED / self-signed certificate in chain".
  Fix: `--compat-options no-certifi` makes yt-dlp use the system trust
  store, which honours SSL_CERT_FILE=/run/hatch/egress-tls/ca-bundle.pem
  (already set in the sandbox env). Do NOT use --no-check-certificates.
- `--comment-max` does not exist in yt-dlp 2026.10.21. Cap comments with
  `--extractor-args youtube:max_comments=N`.
- Comments are returned newest-first by default; top-level comments have
  parent == "root". Author fields are dropped on purpose (anonymised).
"""
import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone


def fetch(video, max_comments=100, yt_dlp="yt-dlp"):
    cmd = [
        yt_dlp,
        "--compat-options", "no-certifi",
        "--extractor-args", f"youtube:max_comments={max_comments}",
        "--write-comments",
        "--write-info-json",
        "--skip-download",
        "--no-warnings",
        "-o", "%(id)s.info.json",
        video,
    ]
    # Run in a temp dir so the .info.json lands somewhere disposable.
    import os
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        proc = subprocess.run(cmd, cwd=td, capture_output=True, text=True,
                              timeout=600)
        if proc.returncode != 0:
            raise RuntimeError(
                f"yt-dlp failed (exit {proc.returncode}):\n"
                f"{proc.stdout[-2000:]}\n{proc.stderr[-2000:]}")
        files = [f for f in os.listdir(td) if f.endswith(".info.json")]
        if not files:
            raise RuntimeError("yt-dlp produced no .info.json")
        with open(os.path.join(td, files[0]), encoding="utf-8") as fh:
            info = json.load(fh)
    comments = []
    for i, c in enumerate(info.get("comments") or []):
        comments.append({
            "index": i,
            "text": (c.get("text") or "").strip(),
            "like_count": c.get("like_count", 0),
            "parent": c.get("parent") or "root",
        })
    return {
        "video_id": info.get("id"),
        "title": info.get("title"),
        "channel": info.get("channel"),
        "comment_count": info.get("comment_count"),
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "comments": comments,
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("video", help="YouTube URL or video ID")
    ap.add_argument("--max-comments", type=int, default=100)
    ap.add_argument("--out", default="comments.json")
    ap.add_argument("--yt-dlp", default="yt-dlp")
    args = ap.parse_args()
    data = fetch(args.video, args.max_comments, args.yt_dlp)
    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)
    print(f"{data['video_id']}: {len(data['comments'])} comments "
          f"(total on video: {data['comment_count']}) -> {args.out}")


if __name__ == "__main__":
    main()
