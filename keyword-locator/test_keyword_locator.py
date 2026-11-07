"""Mock tests for the keyword locator prototype. No network, no API key.

Synthetic segments only — no real video is fetched, so this proves the
matching logic, not a live YouTube lookup. Run: python3 test_keyword_locator.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from keyword_locator import locate_keyword

SEGMENTS = [
    {"start": 0.0, "end": 4.5, "text": "Today we look at how agents pay for APIs."},
    {"start": 4.5, "end": 9.0, "text": "The x402 protocol lets an agent pay in USDC on Base."},
    {"start": 9.0, "end": 13.5, "text": "Search sold far more than transcript in the first report."},
    {"start": 13.5, "end": 18.0, "text": "Agents search, agents pay, and agents keep the receipt."},
    {"start": 18.0, "end": 22.0, "text": "That is the whole story."},
]


def check(name, cond):
    assert cond, name
    print(f"PASS: {name}")


def main():
    # 1. Keyword in several segments, timestamps in order.
    r = locate_keyword(SEGMENTS, "agents")
    check("multi-segment match count == 2", r["match_count"] == 2)
    check("timestamps ordered", [m["start"] for m in r["matches"]] == [0.0, 13.5])
    check("total occurrences counts repeats", r["total_occurrences"] == 4)
    # 2. Case-insensitive.
    r2 = locate_keyword(SEGMENTS, "X402")
    check("case-insensitive match", r2["match_count"] == 1 and r2["matches"][0]["start"] == 4.5)
    # 3. No match is an empty result, not an error.
    r3 = locate_keyword(SEGMENTS, "notpresent")
    check("no match returns empty", r3["match_count"] == 0 and r3["matches"] == [])
    # 4. Empty keyword is rejected.
    try:
        locate_keyword(SEGMENTS, "   ")
        raise AssertionError("empty keyword should raise")
    except ValueError:
        print("PASS: empty keyword raises ValueError")
    # 5. max_matches caps the list.
    r5 = locate_keyword(SEGMENTS, "agents", max_matches=2)
    check("max_matches caps output", r5["match_count"] == 2)
    # 6. Segments without text are skipped, not crashed on.
    r6 = locate_keyword([{"start": 0, "end": 1, "text": ""},
                         {"start": 1, "end": 2, "text": "agents here"}],
                        "agents")
    check("empty segment skipped", r6["match_count"] == 1)
    print("All mock tests green — local prototype only, nothing deployed.")


if __name__ == "__main__":
    main()
