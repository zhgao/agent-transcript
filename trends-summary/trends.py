"""Public hotlist summary prototype — LOCAL ONLY, $0, no deployment.

Built 2026-11-06 as the next step named in the 2026-11-06 daily
earning report: "add a free /v1/trends endpoint (HN Top 10 summary)
on the existing service, first see whether any agent calls it, then
decide whether to charge."

What it does: summarize Hacker News Top N stories (title, link,
score, comment count) from the free public Firebase API
(https://hacker-news.firebaseio.com/v0/), no API key, no account,
no upstream cost. This is the pure-logic prototype; wiring it into
the FastAPI app as /v1/trends is a separate, later decision.

What it does NOT do:
- No deployment: nothing on https://agent-transcript.fly.dev changed.
- No spending, no account, no post, no price set. The report floated
  $0.005/call as a possible paid tier; that is NOT a decision.
- No network in tests: the transport is injected, so tests run on
  synthetic responses and never touch the network. A live HN check is
  a separate, optional step and is NOT required for the mock tests.
- No GitHub trending: GitHub has no official trending API, so this
  prototype covers HN only, exactly as the report scoped it. Do not
  present it as "HN + GitHub trending" until a GitHub source is added.

Rules, kept strict on purpose:
- limit must be 1..30, otherwise ValueError (the report scoped Top 10;
  the cap stops one call from fanning out into hundreds of fetches).
- Items with no title are skipped, not returned half-empty.
- Items with no external URL (e.g. Ask HN) keep url=None and carry
  their HN discussion link instead; nothing invents a URL.
- A transport error propagates instead of returning a fake summary.
"""

TOP_STORIES_URL = "https://hacker-news.firebaseio.com/v0/topstories.json"
ITEM_URL = "https://hacker-news.firebaseio.com/v0/item/{}.json"
HN_ITEM_URL = "https://news.ycombinator.com/item?id={}"

MIN_LIMIT = 1
MAX_LIMIT = 30
DEFAULT_LIMIT = 10


def validate_limit(limit):
    """Top-N must be a whole number in 1..30."""
    if isinstance(limit, bool) or not isinstance(limit, int):
        raise ValueError(f"limit must be an integer: {limit!r}")
    if limit < MIN_LIMIT or limit > MAX_LIMIT:
        raise ValueError(
            f"limit must be {MIN_LIMIT}..{MAX_LIMIT}: {limit!r}")
    return limit


def get_top_ids(transport, limit=DEFAULT_LIMIT):
    """transport(url) -> parsed JSON; returns the first `limit` story ids."""
    validate_limit(limit)
    ids = transport(TOP_STORIES_URL)
    if not isinstance(ids, list):
        raise ValueError(f"topstories did not return a list: {ids!r}")
    return ids[:limit]


def get_item(transport, item_id):
    """transport(url) -> parsed JSON; returns one story dict or None."""
    if isinstance(item_id, bool) or not isinstance(item_id, int):
        raise ValueError(f"item id must be an integer: {item_id!r}")
    item = transport(ITEM_URL.format(item_id))
    if item is None:
        return None
    if not isinstance(item, dict):
        raise ValueError(f"item did not return an object: {item!r}")
    return item


def summarize_item(item, rank):
    """One story -> a fixed-shape summary dict, or None if unusable."""
    if not isinstance(item, dict):
        return None
    title = item.get("title")
    if not title:
        return None
    story_id = item.get("id")
    return {
        "rank": rank,
        "title": title,
        "url": item.get("url"),
        "hn_url": (HN_ITEM_URL.format(story_id)
                   if isinstance(story_id, int) else None),
        "score": item.get("score", 0),
        "comments": item.get("descendants", 0),
        "by": item.get("by"),
    }


def summarize_top(transport, limit=DEFAULT_LIMIT):
    """Top-N HN summary: {"source", "count", "items": [...]}.

    Items that fail to load or have no title are skipped; if every
    item is skipped the result is an empty list, not an error.
    """
    validate_limit(limit)
    ids = get_top_ids(transport, limit)
    items = []
    for rank, item_id in enumerate(ids, start=1):
        try:
            item = get_item(transport, item_id)
        except Exception:
            continue
        summary = summarize_item(item, rank)
        if summary is not None:
            items.append(summary)
    return {"source": "Hacker News", "count": len(items), "items": items}
