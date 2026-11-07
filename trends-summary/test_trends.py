"""Mock tests only — synthetic HN responses, no network, no spend.

Run: python3 test_trends.py
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from trends import (
    DEFAULT_LIMIT,
    HN_ITEM_URL,
    ITEM_URL,
    TOP_STORIES_URL,
    get_item,
    get_top_ids,
    summarize_item,
    summarize_top,
    validate_limit,
)

PASSED = 0


def check(name, cond):
    global PASSED
    assert cond, f"FAILED: {name}"
    PASSED += 1
    print(f"ok: {name}")


def expect_error(name, fn):
    global PASSED
    try:
        fn()
    except (ValueError, RuntimeError):
        PASSED += 1
        print(f"ok: {name}")
        return
    raise AssertionError(f"FAILED (no error raised): {name}")


def fake_transport(responses, calls=None):
    def fetch(url):
        if calls is not None:
            calls.append(url)
        if url not in responses:
            raise RuntimeError(f"unexpected url in test: {url}")
        value = responses[url]
        if isinstance(value, Exception):
            raise value
        return value
    return fetch


# --- fixtures: 3 top ids, one normal story, one Ask HN, one deleted ---
IDS = [111, 222, 333]
RESPONSES = {
    TOP_STORIES_URL: IDS,
    ITEM_URL.format(111): {
        "id": 111, "title": "Show HN: A tiny thing", "url": "https://example.com/tiny",
        "score": 120, "descendants": 45, "by": "someone", "type": "story",
    },
    ITEM_URL.format(222): {
        "id": 222, "title": "Ask HN: How do you test?", "score": 80,
        "descendants": 200, "by": "asker", "type": "story",
    },
    ITEM_URL.format(333): None,  # deleted / missing story
}

# --- validate_limit ---
check("default limit is 10", DEFAULT_LIMIT == 10)
check("limit 1 ok", validate_limit(1) == 1)
check("limit 30 ok", validate_limit(30) == 30)
expect_error("limit 0 rejected", lambda: validate_limit(0))
expect_error("limit 31 rejected", lambda: validate_limit(31))
expect_error("limit '10' rejected", lambda: validate_limit("10"))
expect_error("limit True rejected", lambda: validate_limit(True))

# --- get_top_ids ---
calls = []
t = fake_transport(RESPONSES, calls)
check("top ids sliced to limit", get_top_ids(t, 2) == [111, 222])
check("topstories url fetched", calls[0] == TOP_STORIES_URL)
expect_error("non-list topstories rejected",
             lambda: get_top_ids(fake_transport({TOP_STORIES_URL: {"a": 1}}), 5))

# --- get_item ---
check("item fetched by id", get_item(t, 111)["title"] == "Show HN: A tiny thing")
check("deleted item returns None", get_item(t, 333) is None)
expect_error("non-int item id rejected", lambda: get_item(t, "111"))

# --- summarize_item ---
s = summarize_item(RESPONSES[ITEM_URL.format(111)], 1)
check("normal story keeps title/url/score/comments",
      s == {"rank": 1, "title": "Show HN: A tiny thing",
            "url": "https://example.com/tiny",
            "hn_url": HN_ITEM_URL.format(111),
            "score": 120, "comments": 45, "by": "someone"})
a = summarize_item(RESPONSES[ITEM_URL.format(222)], 2)
check("Ask HN keeps url None and hn_url set",
      a["url"] is None and a["hn_url"] == HN_ITEM_URL.format(222)
      and a["comments"] == 200)
check("title-less item skipped", summarize_item({"id": 9}, 3) is None)
check("non-dict item skipped", summarize_item("nope", 3) is None)

# --- summarize_top (end to end, mocked) ---
result = summarize_top(fake_transport(RESPONSES), 3)
check("source labelled Hacker News", result["source"] == "Hacker News")
check("deleted story skipped, 2 items kept", result["count"] == 2
      and len(result["items"]) == 2)
check("ranks preserved in order",
      [i["rank"] for i in result["items"]] == [1, 2])
check("first item is the top story",
      result["items"][0]["title"] == "Show HN: A tiny thing")

# --- transport errors ---
err_responses = dict(RESPONSES)
err_responses[ITEM_URL.format(111)] = RuntimeError("boom")
r2 = summarize_top(fake_transport(err_responses), 3)
check("failing item skipped, others kept",
      r2["count"] == 1 and r2["items"][0]["rank"] == 2)
expect_error("topstories fetch error propagates",
             lambda: summarize_top(
                 fake_transport({TOP_STORIES_URL: RuntimeError("down")}), 3))
check("empty top list gives empty items",
      summarize_top(fake_transport({TOP_STORIES_URL: []}), 5)
      == {"source": "Hacker News", "count": 0, "items": []})

print(f"\n{PASSED} mock checks passed, 0 failed (no network used)")
