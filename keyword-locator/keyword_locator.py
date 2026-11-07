"""Local prototype only — video keyword locator for agents.

Idea (from the 2026-10-26 daily earning report): an agent gives a video
URL + a keyword and gets back only the timestamped segments containing
that keyword, instead of the whole transcript.

Scope of this prototype, deliberately narrow:
- Pure function over already-fetched transcript segments. No network,
  no YouTube fetch, no paid upstream, no deploy, no posting.
- It does NOT call get_transcript_free here: the test harness feeds it
  synthetic segments, so the test proves the matching logic without
  spending anything or touching the live API.
- No price is set here. The daily report noted $0.005 would be the
  competitive tier, but George has not priced this endpoint — do not
  present any price as decided.

Matching rules (kept simple and honest):
- Case-insensitive substring match per segment.
- One match entry per segment that contains the keyword, in segment
  order, with that segment's start/end timestamps and full segment text.
- total_occurrences counts every occurrence across segments, so a
  segment that repeats the keyword is not under-counted.
"""

from __future__ import annotations


def locate_keyword(segments, keyword, max_matches=20):
    """Return timestamped matches for keyword in transcript segments.

    segments: list of dicts with at least "start", "end", "text".
    keyword: non-empty string.
    Returns dict: {"keyword", "match_count", "total_occurrences",
    "matches": [{"start", "end", "text", "occurrences"}]}.
    No match is an empty matches list, not an error.
    """
    if not isinstance(keyword, str) or not keyword.strip():
        raise ValueError("keyword is required")
    if not isinstance(segments, list):
        raise ValueError("segments must be a list")
    needle = keyword.strip().lower()
    matches = []
    total = 0
    for seg in segments:
        text = (seg or {}).get("text") or ""
        if not text:
            continue
        count = text.lower().count(needle)
        if count == 0:
            continue
        total += count
        matches.append({
            "start": seg.get("start"),
            "end": seg.get("end"),
            "text": text,
            "occurrences": count,
        })
        if len(matches) >= max_matches:
            break
    return {
        "keyword": keyword.strip(),
        "match_count": len(matches),
        "total_occurrences": total,
        "matches": matches,
    }
