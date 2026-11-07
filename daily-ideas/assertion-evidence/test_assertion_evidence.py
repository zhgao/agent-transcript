"""Mock tests for the assertion-evidence locator. No network, no API key.

Synthetic segments only — no real video is fetched, so this proves the
matching/ranking logic, not a live YouTube lookup.
Run: python3 test_assertion_evidence.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from assertion_evidence import locate_assertion, key_terms

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
    # 1. Multi-word assertion matches on key terms, not exact substring.
    r = locate_assertion(SEGMENTS, "agents pay in USDC")
    check("multi-word assertion finds hits", r["match_count"] >= 2)
    check("key terms drop stopwords", r["key_terms"] == ["agents", "pay", "usdc"])
    # 2. Strongest match ranks first (segment 22.0 has all 3 terms, twice).
    check("best match ranks first", r["matches"][0]["start"] == 22.0)
    check("best match lists all terms", r["matches"][0]["matched_terms"] == ["agents", "pay", "usdc"])
    # 3. Exact phrase gets the bonus flag.
    r2 = locate_assertion(SEGMENTS, "pay in USDC")
    check("exact phrase flagged", any(m["exact_phrase"] for m in r2["matches"]))
    # 4. Case-insensitive.
    r3 = locate_assertion(SEGMENTS, "X402 PROTOCOL")
    check("case-insensitive match", r3["match_count"] == 1 and r3["matches"][0]["start"] == 4.5)
    # 5. No match is an empty list, not an error.
    r4 = locate_assertion(SEGMENTS, "quantum banana")
    check("no match returns empty", r4["match_count"] == 0 and r4["matches"] == [])
    # 6. Empty assertion raises ValueError.
    try:
        locate_assertion(SEGMENTS, "   ")
        raise AssertionError("empty assertion should raise")
    except ValueError:
        check("empty assertion raises ValueError", True)
    # 7. Single keyword still works.
    r5 = locate_assertion(SEGMENTS, "transcript")
    check("single keyword works", r5["match_count"] == 1 and r5["matches"][0]["start"] == 9.0)
    # 8. video_url is echoed back.
    r6 = locate_assertion(SEGMENTS, "agents", video_url="https://youtu.be/EXAMPLE")
    check("video_url echoed", r6["video_url"] == "https://youtu.be/EXAMPLE")
    # 9. max_matches caps the list.
    r7 = locate_assertion(SEGMENTS, "agents", max_matches=1)
    check("max_matches caps output", r7["match_count"] == 1 and len(r7["matches"]) == 1)
    # 10. Segments without text are skipped, not crashed on.
    r8 = locate_assertion([{"start": 0, "end": 1, "text": ""},
                           {"start": 1, "end": 2, "text": "agents pay"}],
                          "agents pay")
    check("empty segment skipped", r8["match_count"] == 1)
    # 11. Partial term match still counts (only some key terms present).
    r9 = locate_assertion(SEGMENTS, "agents pay in USDC")
    check("partial match included", any(m["start"] == 0.0 for m in r9["matches"]))
    # 12. key_terms falls back to all words when all are stopwords.
    check("stopword-only fallback", key_terms("it is") == ["it", "is"])
    print(f"All {passed} mock checks green — local prototype only, nothing deployed.")


if __name__ == "__main__":
    main()
