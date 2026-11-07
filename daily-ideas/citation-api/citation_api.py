"""Local prototype only — verifiable citation API for agents.

Idea (2026-11-01 daily idea): an agent asks a question about a video and
gets back the single best timestamped verbatim quote answering it, plus
the video link and start time, plus a confidence note saying whether the
quote is an exact phrase match or only keyword overlap.

Scope, deliberately narrow:
- Pure function over already-fetched transcript segments. No network,
  no YouTube fetch, no paid upstream, no deploy, no posting, no price.
- Scoring prefers segments sharing the most question keywords
  (distinct keywords matched, then total occurrences), with a bonus
  when the question's exact phrase appears verbatim in the segment.
- No match returns None for the citation (not an error); empty question
  raises ValueError.
- Confidence note is honest about its limits: it describes the match
  type, it does not claim the quote is true or that it fully answers
  the question — a human/agent must still judge relevance.

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
    "which", "how", "why", "there", "here", "all", "any", "some", "does",
}

EXACT_PHRASE_BONUS = 10
KEYWORD_WEIGHT = 2


def question_keywords(question: str) -> list[str]:
    """Split a question into meaningful keywords (stopwords dropped).

    Falls back to all words if every word is a stopword.
    """
    words = re.findall(r"[a-z0-9]+", question.lower())
    terms = [w for w in words if w not in STOPWORDS and len(w) >= 2]
    return terms or words


def score_segment(question: str, segment_text: str) -> dict:
    """Score one segment against a question.

    Returns {"score", "matched_keywords", "total_keywords",
    "occurrences", "exact_phrase"}. Score = 2 per distinct keyword
    matched + 1 per extra occurrence + 10 exact-phrase bonus.
    """
    if not isinstance(question, str) or not question.strip():
        raise ValueError("question is required")
    keywords = question_keywords(question)
    text_lower = (segment_text or "").lower()
    phrase = question.strip().lower()
    matched = [k for k in keywords if k in text_lower]
    occurrences = sum(text_lower.count(k) for k in matched)
    exact = bool(phrase) and phrase in text_lower
    score = len(matched) * KEYWORD_WEIGHT + occurrences
    if exact:
        score += EXACT_PHRASE_BONUS
    return {
        "score": score,
        "matched_keywords": matched,
        "total_keywords": len(keywords),
        "occurrences": occurrences,
        "exact_phrase": exact,
    }


def _confidence_note(result: dict) -> str:
    if result["exact_phrase"]:
        return ("exact phrase match: the question phrase appears verbatim "
                "in the quoted segment")
    n, total = len(result["matched_keywords"]), result["total_keywords"]
    return (f"keyword overlap: {n}/{total} question keywords appear in "
            "the quoted segment; verify it actually answers the question")


def find_citation(segments, question, video_url=None):
    """Return the single best timestamped verbatim quote for a question.

    segments: list of dicts with at least "start", "end", "text".
    question: non-empty string. video_url: optional, echoed back.
    Returns None when no segment shares any question keyword, else a dict:
    {"question", "video_url", "start", "end", "quote", "score",
    "matched_keywords", "exact_phrase", "confidence"}.
    Ties break by earliest start time.
    """
    if not isinstance(question, str) or not question.strip():
        raise ValueError("question is required")
    if not isinstance(segments, list):
        raise ValueError("segments must be a list")
    best = None
    for seg in segments:
        text = (seg or {}).get("text") or ""
        if not text:
            continue
        result = score_segment(question, text)
        if not result["matched_keywords"] and not result["exact_phrase"]:
            continue
        start = seg.get("start")
        candidate = {
            "question": question.strip(),
            "video_url": video_url,
            "start": start,
            "end": seg.get("end"),
            "quote": text,
            "score": result["score"],
            "matched_keywords": result["matched_keywords"],
            "exact_phrase": result["exact_phrase"],
            "confidence": _confidence_note(result),
        }
        if (best is None or candidate["score"] > best["score"]
                or (candidate["score"] == best["score"]
                    and (start or 0) < (best["start"] or 0))):
            best = candidate
    return best
