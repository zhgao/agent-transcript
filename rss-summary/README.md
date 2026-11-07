# RSS update-summary — local prototype ($0)

Local prototype for the 2026-11-07 earning report's next step: an agent
passes a public RSS URL, gets the most recent N items with title + link +
one rule-based sentence summary. No paid model, no key, no account.

## What it does

`summarize_feed(feed_xml, source_url, limit=10)` in `rss_summary.py`:
- Parses RSS 2.0 XML, returns `{source, count, items:[{title, link,
  summary, pubDate}]}`.
- Summary = first sentence of the item description (HTML stripped), else
  the title; truncated to 200 chars. Nothing is invented.
- limit capped 1..30; items missing both title and link are skipped;
  invalid XML / empty feed / missing `<channel>` raise instead of
  returning a fake empty result.
- `fetch_feed(url)` fetches a public feed with plain urllib (no key).

## What was verified

- `python3 test_rss_summary.py` — **19/19 mock checks passed, 0 failed**,
  no network used (2026-11-07 ~09:35 Beijing).
- Live check (`LIVE_CHECK.md`, same morning): hnrss frontpage and
  GitHub Blog feed both fetched and parsed, 3 items each, $0.
  Chromium Blog was named in the report as already tested on 2026-11-07
  and was not re-fetched here.

## Honest limits

- hnrss item descriptions are not prose — they read "Article URL: …
  Comments URL: …" — so the first-sentence rule returns link text for
  HN items, not a real summary. A per-source description rule would be
  needed before charging for HN feeds.
- Nothing is deployed to https://agent-transcript.fly.dev, nothing is
  priced, no account created, no post made.
- Decisions remain George's: wire it in as a free endpoint or keep it
  local; price only if agents actually call it.
