"""Public RSS update-summary prototype — local only, $0.

summarize_feed(feed_xml, source_url, limit=N) parses a public RSS 2.0
feed (already-fetched XML string) and returns the most recent items with
a rule-based one-line summary each. No paid model, no key, no account.

Rules, stated plainly:
- Summary = first sentence of the item description, else the title,
  truncated to 200 chars. HTML tags are stripped; nothing is invented.
- Items missing both title and link are skipped, never faked.
- limit is capped 1..30; invalid XML raises, it is never papered over
  with an empty result.
- Fetching is the caller's job (fetch_feed below uses plain urllib);
  tests inject XML directly so they need no network.
"""

import html
import re
import urllib.request
import xml.etree.ElementTree as ET

MAX_LIMIT = 30
SUMMARY_CHARS = 200

_FEED1 = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"><channel>
<title>Example Blog</title><link>https://example.com</link>
<item><title>First post</title><link>https://example.com/1</link>
<description><![CDATA[<p>Hello world. Second sentence here.</p>]]></description>
<pubDate>Mon, 03 Nov 2026 10:00:00 GMT</pubDate></item>
<item><title>Second post</title><link>https://example.com/2</link>
<description>Plain description without HTML. More text follows here.</description>
<pubDate>Tue, 04 Nov 2026 10:00:00 GMT</pubDate></item>
<item><title></title><link></link><description></description></item>
</channel></rss>"""


def _strip_html(text):
    text = re.sub(r"<[^>]+>", " ", text or "")
    text = html.unescape(text)
    return re.sub(r"\s+", " ", text).strip()


def _one_line_summary(description, title):
    text = _strip_html(description) or (title or "").strip()
    if not text:
        return ""
    # First sentence: up to the first . ! ? followed by space/end.
    m = re.search(r"^(.+?[.!?])(\s|$)", text)
    first = m.group(1).strip() if m else text
    if len(first) > SUMMARY_CHARS:
        first = first[:SUMMARY_CHARS].rstrip() + "…"
    return first


def summarize_feed(feed_xml, source_url, limit=10):
    """Parse RSS XML string -> {source, count, items:[{title, link, summary}]}."""
    if not isinstance(limit, int) or isinstance(limit, bool):
        raise ValueError("limit must be an integer")
    if limit < 1 or limit > MAX_LIMIT:
        raise ValueError(f"limit must be 1..{MAX_LIMIT}")
    if not feed_xml or not feed_xml.strip():
        raise ValueError("empty feed")
    root = ET.fromstring(feed_xml)  # raises ParseError on invalid XML
    channel = root.find("channel")
    if channel is None:
        raise ValueError("not an RSS feed: no <channel>")
    items = []
    for node in channel.findall("item"):
        title = (node.findtext("title") or "").strip()
        link = (node.findtext("link") or "").strip()
        if not title and not link:
            continue
        desc = node.findtext("description") or ""
        items.append({
            "title": title or None,
            "link": link or None,
            "summary": _one_line_summary(desc, title),
            "pubDate": (node.findtext("pubDate") or "").strip() or None,
        })
        if len(items) >= limit:
            break
    return {"source": source_url, "count": len(items), "items": items}


def fetch_feed(url, timeout=15):
    """Fetch a public RSS URL, return raw XML text. No key, no account."""
    req = urllib.request.Request(url, headers={"User-Agent": "rss-summary-prototype/0.1"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", errors="replace")
