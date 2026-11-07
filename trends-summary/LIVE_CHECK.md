# Trends summary — live HN check (addendum to README)

Checked 2026-11-06 ~16:30 Beijing, $0, no key, no account.

- `GET https://hacker-news.firebaseio.com/v0/topstories.json` — returned a
  list of story IDs (first IDs 50385272, 50389333, ...), ~1s total for the
  fetch in this run.
- `GET https://hacker-news.firebaseio.com/v0/item/1.json` — returned the
  "Y Combinator" story object (by pg, score 57), confirming item fetches
  work too.
- Mock tests re-run same time: `python3 test_trends.py` — 24/24 passed.

What this does NOT prove: sustained latency/failure rate (one fetch only),
or that any agent will call a /v1/trends endpoint. Still not deployed;
still HN only; still unpriced. Decisions remain George's (wire in as a
free endpoint or keep local; price only if agents actually call it).
