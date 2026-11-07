"""Cluster complaint categories across videos (pure functions, no I/O).

Input: a list of per-video dicts, each with:
    {"video_id": str, "comments": [{"text": str, "categories": [str, ...]}]}
where "categories" are hand-assigned (or classifier-assigned) complaint
tags for that comment; a comment with no complaints has an empty list.

Output of cluster_videos(): per-category counts per video, how many videos
each category appears in, and a cluster verdict:
    - "strong"  : category appears in all videos
    - "partial" : category appears in 2 of 3 videos (generalises to >=2
                  and < all when more videos are supplied)
    - "single"  : category appears in only one video
A category "clusters" if it appears in >= 2 videos.

The counting rule: one comment contributes at most 1 to a category even
if it mentions it twice; a comment CAN contribute to several categories.
"""

CATEGORIES = [
    "battery",       # battery life degrades / dies / far below advertised
    "price",         # too expensive / "not really budget"
    "fit",           # falls out / uncomfortable / hurts / wrong size
    "reliability",   # breaks / one side dies / charging defect / QC
    "connectivity",  # Bluetooth drops / won't pair / won't turn on-off
    "mic",           # mic / call quality bad
    "anc",           # noise cancelling weak / faulty
    "volume",        # too quiet / channel imbalance
    "controls",      # app / software / tap-press controls bad
    "lost",          # lost an earbud (falls out / no tracking)
]


def count_categories(comments):
    """Count complaint mentions per category in one video's comments.

    comments: iterable of {"categories": [...]} dicts.
    Returns {category: count} including zero counts for known categories.
    """
    counts = {c: 0 for c in CATEGORIES}
    for comment in comments:
        for cat in set(comment.get("categories") or []):
            if cat in counts:
                counts[cat] += 1
            else:  # unknown tag: still count it, don't crash
                counts[cat] = counts.get(cat, 0) + 1
    return counts


def cluster_videos(videos):
    """Cluster complaint categories across a list of per-video dicts.

    Returns:
      {"per_video": {video_id: {category: count, ...}, ...},
       "videos_with_category": {category: n_videos},
       "verdict": {category: "strong" | "partial" | "single"},
       "clustered": [categories appearing in >= 2 videos],
       "complaint_rate": {video_id: (n_complaint_comments, n_examined)}}
    """
    n = len(videos)
    per_video = {}
    complaint_rate = {}
    for v in videos:
        comments = v.get("comments") or []
        top_level = [c for c in comments
                     if (c.get("parent") or "root") in ("root", None)]
        examined = top_level if top_level else comments
        per_video[v["video_id"]] = count_categories(examined)
        n_complaint = sum(1 for c in examined if c.get("categories"))
        complaint_rate[v["video_id"]] = (n_complaint, len(examined))

    videos_with = {c: 0 for c in CATEGORIES}
    for counts in per_video.values():
        for cat, k in counts.items():
            if k > 0:
                videos_with[cat] = videos_with.get(cat, 0) + 1

    verdict = {}
    for cat, k in videos_with.items():
        if k >= n and n > 0:
            verdict[cat] = "strong"
        elif k >= 2:
            verdict[cat] = "partial"
        else:
            verdict[cat] = "single"

    return {
        "per_video": per_video,
        "videos_with_category": videos_with,
        "verdict": verdict,
        "clustered": sorted(c for c, k in videos_with.items() if k >= 2),
        "complaint_rate": complaint_rate,
    }
