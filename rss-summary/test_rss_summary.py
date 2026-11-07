"""Mock tests for rss_summary.py — no network used."""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from rss_summary import summarize_feed, _FEED1

passed = failed = 0

def check(name, cond):
    global passed, failed
    if cond:
        passed += 1
        print(f"ok: {name}")
    else:
        failed += 1
        print(f"FAIL: {name}")

# 1. Basic parse: 2 usable items, empty item skipped
r = summarize_feed(_FEED1, "https://example.com/feed.xml", limit=10)
check("two usable items, empty item skipped", r["count"] == 2 and len(r["items"]) == 2)
check("source echoed back", r["source"] == "https://example.com/feed.xml")

# 2. HTML stripped, first sentence only as summary
check("html stripped, first sentence summary",
      r["items"][0]["summary"] == "Hello world.")
check("title/link kept", r["items"][0]["title"] == "First post"
      and r["items"][0]["link"] == "https://example.com/1")

# 3. Plain description, first sentence
check("plain description first sentence",
      r["items"][1]["summary"] == "Plain description without HTML.")

# 4. pubDate kept
check("pubDate kept", r["items"][0]["pubDate"] == "Mon, 03 Nov 2026 10:00:00 GMT")

# 5. limit slicing
r1 = summarize_feed(_FEED1, "https://example.com/feed.xml", limit=1)
check("limit=1 returns one item", r1["count"] == 1)

# 6. limit validation
for bad in (0, 31, -1, "10", None, True):
    try:
        summarize_feed(_FEED1, "https://example.com/feed.xml", limit=bad)
        check(f"limit={bad!r} rejected", False)
    except ValueError:
        check(f"limit={bad!r} rejected", True)

# 7. Empty feed rejected
try:
    summarize_feed("", "https://example.com/feed.xml")
    check("empty feed rejected", False)
except ValueError:
    check("empty feed rejected", True)

# 8. Invalid XML propagates, not faked
try:
    summarize_feed("<rss><channel><item>", "https://example.com/feed.xml")
    check("invalid XML raises", False)
except Exception:
    check("invalid XML raises", True)

# 9. No <channel> rejected
try:
    summarize_feed("<rss version='2.0'></rss>", "https://example.com/feed.xml")
    check("missing channel rejected", False)
except ValueError:
    check("missing channel rejected", True)

# 10. Item with no description falls back to title as summary
feed2 = """<?xml version="1.0"?><rss version="2.0"><channel>
<item><title>Only a title</title><link>https://example.com/9</link></item>
</channel></rss>"""
r2 = summarize_feed(feed2, "https://example.com/feed.xml")
check("no description falls back to title",
      r2["count"] == 1 and r2["items"][0]["summary"] == "Only a title")

# 11. Long description truncated to ~200 chars, not cut mid-word silently
long_desc = "Word " * 100 + "end."
feed3 = ("<?xml version='1.0'?><rss version='2.0'><channel><item>"
         "<title>T</title><link>https://example.com/3</link>"
         f"<description>{long_desc}</description></item></channel></rss>")
r3 = summarize_feed(feed3, "https://example.com/feed.xml")
check("long summary truncated with ellipsis",
      len(r3["items"][0]["summary"]) <= 201 and r3["items"][0]["summary"].endswith("…"))

# 12. Link-only item (no title) kept with title None
feed4 = ("<?xml version='1.0'?><rss version='2.0'><channel><item>"
         "<link>https://example.com/only-link</link>"
         "<description>Something happened.</description></item></channel></rss>")
r4 = summarize_feed(feed4, "https://example.com/feed.xml")
check("link-only item kept, title None",
      r4["count"] == 1 and r4["items"][0]["title"] is None)

print(f"\n{passed} mock checks passed, {failed} failed (no network used)")
sys.exit(1 if failed else 0)
