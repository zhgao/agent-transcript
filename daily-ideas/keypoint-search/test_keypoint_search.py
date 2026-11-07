"""Mock tests for key-point timestamp search. No network, no API key.

Synthetic segments only — no real video is fetched, so this proves the
matching/ranking/summary logic, not a live YouTube lookup.
Run: python3 test_keypoint_search.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from keypoint_search import search_keypoints, summarize, topic_terms

SEGMENTS = [
    {"start": 0.0, "end": 4.5, "text": "Today we look at how agents pay for APIs."},
    {"start": 4.5, "end": 9.0, "text": "The x402 protocol lets an agent pay in USDC on Base."},
    {"start": 9.0, "end": 13.5, "text": "Search sold far more than transcript in the first report."},
    {"start": 13.5, "end": 18.0, "text": "Agents search, agents pay, and agents keep the receipt."},
    {"start": 18.0, "end": 22.0, "text": "That is the whole story."},
    {"start": 22.0, "end": 26.0, "text": "Agents can pay in USDC and also pay in USDC again."},
    {"start": 26.0, "end": 30.0, "text": "Payment rails matter because every agent transaction needs a receipt, "
     "a settlement layer, a stable currency, and a way to prove the money moved at all."},
]

passed = 0


def check(name, cond):
    global passed
    assert cond, name
    passed += 1
    print(f"PASS: {name}")


def main():
    # 1. Single keyword returns ordered timestamped hits.
    r = search_keypoints(SEGMENTS, "agents")
    check("keyword finds hits", r["match_count"] == 3)
    check("hits ordered by score then start", [m["start"] for m in r["matches"]] == [13.5, 0.0, 22.0])
    # 2. Multi-term topic matches segments containing any term, best first.
    r2 = search_keypoints(SEGMENTS, "agent payment USDC")
    check("multi-term topic finds hits", r2["match_count"] >= 3)
    check("multi-term best hit first", r2["matches"][0]["start"] == 22.0)
    check("topic terms split", r2["key_terms"] == ["agent", "payment", "usdc"])
    # 3. Summary line is the first ~120 chars, cut at a word boundary.
    long_hit = next(m for m in search_keypoints(SEGMENTS, "payment")["matches"] if m["start"] == 26.0)
    check("summary truncated to ~120 chars", len(long_hit["summary"]) <= 121)
    check("summary ends with ellipsis", long_hit["summary"].endswith("…"))
    check("summary is a prefix of the text", SEGMENTS[6]["text"].startswith(long_hit["summary"][:-1].rstrip()))
    # 4. Short text summary is unchanged.
    check("short summary unchanged", summarize("Agents search.") == "Agents search.")
    # 5. No match is an empty list, not an error.
    r3 = search_keypoints(SEGMENTS, "quantum banana")
    check("no match returns empty", r3["match_count"] == 0 and r3["matches"] == [])
    # 6. Empty topic raises ValueError.
    try:
        search_keypoints(SEGMENTS, "   ")
        raise AssertionError("empty topic should raise")
    except ValueError:
        check("empty topic raises ValueError", True)
    # 7. Case-insensitive.
    r4 = search_keypoints(SEGMENTS, "X402")
    check("case-insensitive match", r4["match_count"] == 1 and r4["matches"][0]["start"] == 4.5)
    # 8. video_url is echoed back.
    r5 = search_keypoints(SEGMENTS, "agents", video_url="https://youtu.be/EXAMPLE")
    check("video_url echoed", r5["video_url"] == "https://youtu.be/EXAMPLE")
    # 9. max_matches caps the list.
    r6 = search_keypoints(SEGMENTS, "agents", max_matches=1)
    check("max_matches caps output", r6["match_count"] == 1 and len(r6["matches"]) == 1)
    # 10. Segments without text are skipped, not crashed on.
    r7 = search_keypoints([{"start": 0, "end": 1, "text": ""},
                           {"start": 1, "end": 2, "text": "agents here"}],
                          "agents")
    check("empty segment skipped", r7["match_count"] == 1)
    # 11. topic_terms drops stopwords.
    check("topic terms drop stopwords", topic_terms("the future of agents") == ["future", "agents"])
    print(f"All {passed} mock checks green — local prototype only, nothing deployed.")


if __name__ == "__main__":
    main()
