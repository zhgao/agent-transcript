# Assertion-Evidence Locator — local prototype

Idea (2026-10-28 daily idea): an agent asserts something about a video and
gets back only the timestamped segments where that assertion is spoken,
with verbatim text — evidence, not a summary.

## What it does

`assertion_evidence.py` — `locate_assertion(segments, assertion, video_url=None, max_matches=10)`

- Input: an assertion string (or keywords) + transcript segments
  (`{"start", "end", "text"}`, same shape as `keyword-locator`).
- Output: `{"assertion", "key_terms", "video_url", "match_count", "matches"}`,
  where each match is `{"start", "end", "text", "score", "matched_terms",
  "exact_phrase"}`, ranked by match strength.
- Multi-word assertions match on key terms (stopwords dropped), not just
  exact substring. Score = 10 per distinct key term matched + 1 per
  occurrence + 25 exact-phrase bonus; ties break by earliest start.
- No match → empty `matches` list, not an error. Empty assertion → `ValueError`.

## Tests

`python3 test_assertion_evidence.py` — **14/14 mock checks pass**
(synthetic segments only; covers ranking, exact-phrase flag, case-insensitivity,
no-match, empty assertion, single keyword, `video_url` echo, `max_matches`,
empty-segment skip, partial-term match, stopword-only fallback).

## Honest limits

- Local prototype only. Not deployed, not priced, no buyer demand proven.
- Matching is substring-based over words: it finds where terms are *spoken*,
  it does not verify the assertion is *true*, and it cannot tell whether a
  segment supports or contradicts the claim.
- No live-video self-test was run for this prototype (its stated next step
  was the logic itself); the sibling prototypes' live tests hit the sandbox
  YouTube IP block on most videos (see `../citation-api/README.md`).
- $0 spent. No network, no paid services, no accounts, no posting.
