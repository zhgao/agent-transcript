"""Local prototype only — video assertion-evidence locator for agents.

Idea (2026-10-28 daily idea): an agent asserts something about a video
("the speaker says agents pay in USDC") and gets back only the timestamped
segments where that assertion is actually spoken, with verbatim text —
evidence, not a summary.

Scope, deliberately narrow:
- Pure function over already-fetched transcript segments. No network,
  no YouTube fetch, no paid upstream, no deploy, no posting, no price.
- Multi-word assertions match on key terms, not just exact substring:
  stopwords are dropped, remaining terms are matched case-insensitively
  per segment, and hits are ranked by match strength (distinct key terms
  matched, then total term occurrences, then exact-phrase bonus).
- No match is an empty matches list, not an error.
- Empty assertion raises ValueError.

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
    "which", "how", "why", "there", "here", "all", "any", "some", "said",
    "says", "say",
}


def key_terms(assertion: str) -> list[str]:
    """Split an assertion into its meaningful search terms.

    Lowercases, keeps word characters, drops stopwords. If every word is
    a stopword (e.g. "it is"), falls back to all words so the query is
    still searchable instead of silently matching nothing.
    """
    words = re.findall(r"[a-z0-9]+", assertion.lower())
    terms = [w for w in words if w not in STOPWORDS and len(w) >= 2]
    return terms or words


def _score_segment(text_lower: str, terms: list[str], phrase: str) -> dict:
    matched = [t for t in terms if t in text_lower]
    occurrences = sum(text_lower.count(t) for t in matched)
    exact = bool(phrase) and phrase in text_lower
    # Distinct terms matter most; occurrences break ties; exact phrase wins.
    score = len(matched) * 10 + occurrences + (25 if exact else 0)
    return {"matched_terms": matched, "occurrences": occurrences,
            "exact_phrase": exact, "score": score}


def locate_assertion(segments, assertion, video_url=None, max_matches=10):
    """Return timestamped evidence segments for an assertion.

    segments: list of dicts with at least "start", "end", "text".
    assertion: non-empty string (a claim or keywords about the video).
    video_url: optional, echoed back so the caller can link each hit.
    Returns dict: {"assertion", "key_terms", "video_url", "match_count",
    "matches": [{"start", "end", "text", "score", "matched_terms",
    "exact_phrase"}]} ranked by score desc, then start asc.
    No match is an empty matches list, not an error.
    """
    if not isinstance(assertion, str) or not assertion.strip():
        raise ValueError("assertion is required")
    if not isinstance(segments, list):
        raise ValueError("segments must be a list")
    phrase = assertion.strip().lower()
    terms = key_terms(assertion)
    if not terms:
        raise ValueError("assertion is required")
    scored = []
    for seg in segments:
        text = (seg or {}).get("text") or ""
        if not text:
            continue
        s = _score_segment(text.lower(), terms, phrase)
        if not s["matched_terms"] and not s["exact_phrase"]:
            continue
        scored.append({
            "start": seg.get("start"),
            "end": seg.get("end"),
            "text": text,
            "score": s["score"],
            "matched_terms": s["matched_terms"],
            "exact_phrase": s["exact_phrase"],
        })
    scored.sort(key=lambda m: (-m["score"], m["start"] if m["start"] is not None else 0))
    return {
        "assertion": assertion.strip(),
        "key_terms": terms,
        "video_url": video_url,
        "match_count": len(scored[:max_matches]),
        "matches": scored[:max_matches],
    }
