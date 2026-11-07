"""Local prototype only — key-point timestamp search for agents.

Idea (2026-11-03 daily idea): an agent gives a topic/keyword and a
subtitled public video and gets back the ordered timestamped segments
where that topic is discussed, each with a short summary line.

Scope, deliberately narrow:
- Pure function over already-fetched transcript segments. No network,
  no YouTube fetch, no paid upstream, no deploy, no posting, no price.
- Topic-level, not single-keyword: multi-term topics are split into key
  terms (stopwords dropped), a segment matches if it contains any term,
  and hits rank by distinct terms matched, then total occurrences,
  then start time.
- Each hit carries a summary line: the first ~120 chars of the segment,
  cut at a word boundary with an ellipsis when truncated.
- No match is an empty matches list, not an error; empty topic raises
  ValueError.

Segment shape (same as keyword-locator): dicts with "start", "end", "text".
"""

from __future__ import annotations

import re

STOPWORDS = {
    "a", "an", "the", "is", "are", "was", "were", "be", "been", "being",
    "it", "its", "this", "that", "these", "those", "of", "to", "in", "on",
    "for", "and", "or", "with", "by", "as", "at", "from", "into", "about",
    "do", "does", "did", "has", "have", "had", "will", "would", "can",
    "could", "should", "you", "we", "they", "he", "she", "i", "not", "no",
    "so", "if", "then", "than", "but", "when", "where", "who", "what",
    "which", "how", "why", "there", "here", "all", "any", "some",
}

SUMMARY_LIMIT = 120


def topic_terms(topic: str) -> list[str]:
    """Split a topic into meaningful search terms (stopwords dropped)."""
    words = re.findall(r"[a-z0-9]+", topic.lower())
    terms = [w for w in words if w not in STOPWORDS and len(w) >= 2]
    return terms or words


def summarize(text: str, limit: int = SUMMARY_LIMIT) -> str:
    """First ~limit chars of a segment, cut at a word boundary.

    Short text is returned unchanged; longer text is cut at the last
    space before the limit and given a trailing ellipsis.
    """
    text = (text or "").strip()
    if len(text) <= limit:
        return text
    cut = text[:limit].rsplit(" ", 1)[0]
    return (cut or text[:limit]).rstrip() + "…"


def search_keypoints(segments, topic, video_url=None, max_matches=20):
    """Return ordered timestamped segments discussing a topic.

    segments: list of dicts with at least "start", "end", "text".
    topic: non-empty string (a keyword or multi-term topic).
    video_url: optional, echoed back so the caller can link each hit.
    Returns dict: {"topic", "key_terms", "video_url", "match_count",
    "matches": [{"start", "end", "text", "summary", "score",
    "matched_terms"}]} ranked by score desc, then start asc.
    No match is an empty matches list, not an error.
    """
    if not isinstance(topic, str) or not topic.strip():
        raise ValueError("topic is required")
    if not isinstance(segments, list):
        raise ValueError("segments must be a list")
    terms = topic_terms(topic)
    if not terms:
        raise ValueError("topic is required")
    scored = []
    for seg in segments:
        text = (seg or {}).get("text") or ""
        if not text:
            continue
        lower = text.lower()
        matched = [t for t in terms if t in lower]
        if not matched:
            continue
        occurrences = sum(lower.count(t) for t in matched)
        scored.append({
            "start": seg.get("start"),
            "end": seg.get("end"),
            "text": text,
            "summary": summarize(text),
            "score": len(matched) * 10 + occurrences,
            "matched_terms": matched,
        })
    scored.sort(key=lambda m: (-m["score"], m["start"] if m["start"] is not None else 0))
    return {
        "topic": topic.strip(),
        "key_terms": terms,
        "video_url": video_url,
        "match_count": len(scored[:max_matches]),
        "matches": scored[:max_matches],
    }
