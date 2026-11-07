# Trends summary — LOCAL PROTOTYPE ONLY

Built 2026-11-06 (Beijing morning) as the next step named in the
2026-11-06 daily earning report: "add a free /v1/trends endpoint
(HN Top 10 summary) on the existing service, first see whether any
agent calls it, then decide whether to charge."

What it is: `trends.py:summarize_top(transport, limit=10)` — given an
injected JSON fetcher, return the Hacker News Top N as
`{source, count, items: [{rank, title, url, hn_url, score, comments,
by}]}`. Upstream is the free public HN Firebase API, no key, no
account, no upstream cost. Limit is capped at 1..30; Ask HN items
keep `url=None` with their discussion link; deleted items and failed
fetches are skipped, never faked.

What it is NOT:
- Not deployed. Nothing on https://agent-transcript.fly.dev changed;
  there is no /v1/trends route on the live service yet.
- Not a live HN lookup. Tests use synthetic responses only — no live
  latency/failure rate measured yet.
- Not HN + GitHub trending. GitHub has no official trending API, so
  this prototype covers HN only, exactly as the report scoped it.
- Not priced. $0.005/call was floated in the report as a possible
  paid tier, not a decision.
- Not a claim of agent demand: the report's case rests on Bazaar
  30-day data (data/news reads sell in small $0.001–$0.008 slices),
  which is a market signal, not proof anyone will call this endpoint.

Test: `python3 test_trends.py` — 24/24 mock checks green
(2026-11-06, no network used). Re-verified 2026-11-07: 24/24 green.

## Live upstream check (2026-11-07, $0)
HN Firebase API `https://hacker-news.firebaseio.com/v0/topstories.json`
fetched successfully and returned 500 story IDs — the upstream is
reachable and needs no key. Item-level fetch (title/score per story)
was not run in this check; the mock tests already cover item parsing
and skipping of deleted/failed items.

Next decisions, all George's, none taken here:
1. Wire it into the FastAPI app as a free /v1/trends endpoint, or
   keep it a local prototype.
2. Price it at all — free first per the report, charge only if agents
   actually call it.
3. Whether a live HN check (one real fetch, still $0) should run
   before wiring it in, to record real latency/failure rate.
