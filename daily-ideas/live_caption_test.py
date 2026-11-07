"""One-off live self-test for citation-api and keypoint-search (2026-11-07).

Fetches English caption tracks with yt-dlp using compat_opts no-certifi
(the sandbox egress proxy MITMs TLS; certifi's bundle lacks the Hatch CA,
which is why the plain youtube-transcript-api / yt-dlp paths failed
earlier). Parses VTT into segments and runs the two prototypes' functions.
No files in the prototypes are modified; results are printed only.
"""
import json
import os
import re
import sys
import tempfile

sys.path.insert(0, os.path.expanduser(
    "~/workspace/agent-sales-exploration/daily-ideas/citation-api"))
sys.path.insert(0, os.path.expanduser(
    "~/workspace/agent-sales-exploration/daily-ideas/keypoint-search"))
sys.path.insert(0, os.path.expanduser(
    "~/workspace/agent-sales-exploration/.venv/lib/python3.12/site-packages"))

from citation_api import find_citation          # noqa: E402
from keypoint_search import search_keypoints    # noqa: E402
import yt_dlp                                   # noqa: E402

VIDEOS = [
    ("dQw4w9WgXcQ", "Rick Astley — Never Gonna Give You Up",
     "what does he promise never to do", "never gonna give you up"),
    ("jNQXAC9IVRw", "Me at the zoo",
     "what does he say about the elephants", "elephants"),
    ("9bZkp7q19f0", "PSY — Gangnam Style",
     "what is Gangnam style", "Gangnam"),
    ("aqz-KE-bpKQ", "Big Buck Bunny",
     "what happens in the story", "bunny"),
    ("_OBlgSz8sSM", "Charlie bit my finger",
     "what does Harry say", "bit"),
]


def ts_to_sec(ts):
    h, m, s = ts.split(":")
    return int(h) * 3600 + int(m) * 60 + float(s.replace(",", "."))


def parse_vtt(path):
    segments = []
    text = open(path, encoding="utf-8", errors="ignore").read()
    blocks = re.split(r"\n\s*\n", text)
    for b in blocks:
        lines = [ln.strip() for ln in b.strip().splitlines() if ln.strip()]
        if len(lines) < 2:
            continue
        m = re.match(r"([\d:,.]+)\s+-->\s+([\d:,.]+)", lines[0])
        if not m:
            continue
        seg_text = " ".join(lines[1:])
        seg_text = re.sub(r"<[^>]+>", "", seg_text).strip()
        if seg_text:
            segments.append({"start": ts_to_sec(m.group(1)),
                             "end": ts_to_sec(m.group(2)),
                             "text": seg_text})
    return segments


def fetch_segments(video_id):
    with tempfile.TemporaryDirectory() as td:
        opts = {
            "compat_opts": {"no-certifi"},
            "skip_download": True,
            "quiet": True,
            "no_warnings": True,
            "writesubtitles": True,
            "writeautomaticsub": True,
            "subtitleslangs": ["en"],
            "subtitlesformat": "vtt/best",
            "outtmpl": os.path.join(td, "%(id)s"),
        }
        with yt_dlp.YoutubeDL(opts) as y:
            y.download([f"https://www.youtube.com/watch?v={video_id}"])
        vtts = [f for f in os.listdir(td) if f.endswith(".vtt")]
        if not vtts:
            return None, "no English caption track downloaded"
        # Prefer manual captions over auto-generated.
        vtts.sort(key=lambda f: (".auto." in f, f))
        return parse_vtt(os.path.join(td, vtts[0])), f"via {vtts[0]}"


def main():
    for vid, title, question, topic in VIDEOS:
        print(f"\n### {vid} — {title}")
        try:
            segs, how = fetch_segments(vid)
        except Exception as exc:  # noqa: BLE001
            print(f"FETCH FAIL: {exc}".strip()[:300])
            continue
        if not segs:
            print(f"FETCH FAIL: {how}")
            continue
        print(f"FETCH OK ({how}): {len(segs)} segments")
        url = f"https://www.youtube.com/watch?v={vid}"
        cit = find_citation(segs, question, video_url=url)
        if cit:
            print(f"CITATION Q={question!r} -> start={cit['start']:.2f} "
                  f"score={cit['score']} confidence={cit['confidence']!r} "
                  f"quote={cit['quote'][:120]!r}")
        else:
            print(f"CITATION Q={question!r} -> no match")
        kp = search_keypoints(segs, topic, video_url=url)
        hits = kp["matches"]
        print(f"KEYPOINT topic={topic!r} -> {len(hits)} hits"
              + (f", first at {hits[0]['start']:.2f}s: "
                 f"{hits[0]['text'][:100]!r}" if hits else ""))


if __name__ == "__main__":
    main()
