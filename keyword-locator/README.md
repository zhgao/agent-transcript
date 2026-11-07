# Keyword locator — LOCAL PROTOTYPE ONLY

Built 2026-10-26 (Beijing, midday) as the next step named in the
2026-10-26 daily earning report: "locally build a video keyword-locator
endpoint prototype and mock-test it, without touching the live site."

What it is: `keyword_locator.py:locate_keyword(segments, keyword)` —
given transcript segments, return only the segments containing the
keyword, with start/end timestamps, in order. Case-insensitive
substring match; no match returns an empty list, not an error.

What it is NOT:
- Not deployed. Nothing on https://agent-transcript.fly.dev changed.
- Not a live YouTube lookup. Tests use synthetic segments only.
- Not priced. No price for this endpoint has been decided by George.
- Not a claim of agent demand: the daily report itself said demand
  here is inferred, not proven, and the price floor is already low.

Test: `python3 test_keyword_locator.py` — all mock checks green
(2026-10-26, re-run after fixing a test expectation; the code was
unchanged by that fix).

Next decisions, all George's, none taken here:
1. Wire it to the free transcript layer (local first) or keep it
   as a standalone prototype.
2. Price it, if at all — the report noted $0.005 would be the
   competitive tier, but that is not a decision.
3. Deploy the already-built $0.005 paid YouTube search first or
   this — paid search is still local-only (live site returned
   {"detail":"Not Found"} for /agent/v1/youtube-search-paid on
   2026-10-26 12:33 Beijing; free search is live and returned
   3 results for Rick Astley).
