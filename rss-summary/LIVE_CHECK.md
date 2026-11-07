# RSS summary — live feed check

Checked 2026-11-07 ~09:35 Beijing, $0, no key, no account.

- `GET https://hnrss.org/frontpage` — fetched and parsed, 3 items
  returned. First item: "Libghostty 1.0". Note: its description is
  "Article URL: … Comments URL: …", so the rule-based summary is link
  text, not prose — a per-source rule would be needed for HN feeds.
- `GET https://github.blog/feed/` — fetched and parsed, 3 items
  returned. First item: "Beyond code generation: A developer's guide
  to agentic engineering", summary "Writing code got faster."
- Chromium Blog was already verified in the 2026-11-07 earning report
  and was not re-fetched here.

What this does NOT prove: sustained latency/failure rate (one fetch
each), or that any agent will call an RSS-summary endpoint. Still not
deployed; still unpriced.
