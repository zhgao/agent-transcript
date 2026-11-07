"""Mock tests for the verifiable citation API. No network, no API key.

Synthetic segments only — no real video is fetched, so this proves the
scoring/selection logic, not a live YouTube lookup.
Run: python3 test_citation_api.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from citation_api import find_citation, score_segment, question_keywords

SEGMENTS = [
    {"start": 0.0, "end": 4.5, "text": "Today we look at how agents pay for APIs."},
    {"start": 4.5, "end": 9.0, "text": "The x402 protocol lets an agent pay in USDC on Base."},
    {"start": 9.0, "end": 13.5, "text": "Search sold far more than transcript in the first report."},
    {"start": 13.5, "end": 18.0, "text": "Agents search, agents pay, and agents keep the receipt."},
    {"start": 18.0, "end": 22.0, "text": "That is the whole story."},
    {"start": 22.0, "end": 26.0, "text": "Agents can pay in USDC and also pay in USDC again."},
]

passed = 0


def check(name, cond):
    global passed
    assert cond, name
    passed += 1
    print(f"PASS: {name}")


def main():
    # 1. Best quote is the segment sharing the most question keywords.
    c = find_citation(SEGMENTS, "how do agents pay in USDC")
    check("best citation found", c is not None)
    check("best citation is strongest segment", c["start"] == 22.0)
    check("quote is verbatim segment text", c["quote"] == SEGMENTS[5]["text"])
    # 2. Confidence note reports keyword overlap (not exact phrase here).
    check("confidence notes keyword overlap", "keyword overlap" in c["confidence"])
    check("matched keywords listed", set(c["matched_keywords"]) == {"agents", "pay", "usdc"})
    # 3. Exact phrase match gets the exact-phrase confidence note.
    c2 = find_citation(SEGMENTS, "pay in USDC")
    check("exact phrase flagged", c2["exact_phrase"] is True)
    check("exact confidence note", "exact phrase match" in c2["confidence"])
    # 4. Scoring prefers more shared keywords over fewer.
    s_many = score_segment("agents pay USDC", SEGMENTS[5]["text"])
    s_few = score_segment("agents pay USDC", SEGMENTS[0]["text"])
    check("more shared keywords scores higher", s_many["score"] > s_few["score"])
    # 5. Exact-phrase bonus: same keywords, phrase present wins.
    s_exact = score_segment("pay in USDC", "An agent can pay in USDC today.")
    s_noexact = score_segment("pay in USDC", "An agent can pay with USDC today.")
    check("exact-phrase bonus applies", s_exact["score"] > s_noexact["score"])
    # 6. No match returns None, not an error.
    check("no match returns None", find_citation(SEGMENTS, "quantum banana") is None)
    # 7. Empty question raises ValueError.
    try:
        find_citation(SEGMENTS, "   ")
        raise AssertionError("empty question should raise")
    except ValueError:
        check("empty question raises ValueError", True)
    # 8. video_url and start time are returned for linking.
    c3 = find_citation(SEGMENTS, "x402 protocol", video_url="https://youtu.be/EXAMPLE")
    check("video_url echoed", c3["video_url"] == "https://youtu.be/EXAMPLE")
    check("start time returned", c3["start"] == 4.5)
    # 9. Case-insensitive matching.
    c4 = find_citation(SEGMENTS, "X402 PROTOCOL")
    check("case-insensitive citation", c4 is not None and c4["start"] == 4.5)
    # 10. Empty-text segments are skipped, not crashed on.
    c5 = find_citation([{"start": 0, "end": 1, "text": ""},
                        {"start": 1, "end": 2, "text": "agents pay"}],
                       "agents pay")
    check("empty segment skipped", c5 is not None and c5["start"] == 1)
    # 11. question_keywords drops stopwords.
    check("question keywords drop stopwords", question_keywords("how do agents pay") == ["agents", "pay"])
    print(f"All {passed} mock checks green — local prototype only, nothing deployed.")


if __name__ == "__main__":
    main()
