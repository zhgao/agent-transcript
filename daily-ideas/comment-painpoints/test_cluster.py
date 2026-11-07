"""Unit tests for cluster.py — synthetic comments only, no network."""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cluster import count_categories, cluster_videos


def c(*cats):
    return {"text": "synthetic", "categories": list(cats)}


def test_count_dedupes_within_comment():
    # One comment mentioning battery twice still counts once.
    counts = count_categories([c("battery", "battery"), c("battery")])
    assert counts["battery"] == 2, counts
    assert counts["price"] == 0


def test_count_multi_category_comment():
    counts = count_categories([c("battery", "fit"), c("fit")])
    assert counts["battery"] == 1 and counts["fit"] == 2


def test_cluster_strong_partial_single():
    videos = [
        {"video_id": "v1", "comments": [c("battery", "price"), c("fit")]},
        {"video_id": "v2", "comments": [c("battery"), c("anc")]},
        {"video_id": "v3", "comments": [c("battery", "price"), c("mic")]},
    ]
    r = cluster_videos(videos)
    assert r["verdict"]["battery"] == "strong", r["verdict"]
    assert r["verdict"]["price"] == "partial", r["verdict"]
    assert r["verdict"]["fit"] == "single", r["verdict"]
    assert r["verdict"]["anc"] == "single", r["verdict"]
    assert set(r["clustered"]) == {"battery", "price"}, r["clustered"]
    assert r["complaint_rate"] == {"v1": (2, 2), "v2": (2, 2), "v3": (2, 2)}


def test_cluster_no_cluster():
    videos = [
        {"video_id": "v1", "comments": [c("battery")]},
        {"video_id": "v2", "comments": [c("price")]},
        {"video_id": "v3", "comments": [c("fit")]},
    ]
    r = cluster_videos(videos)
    assert r["clustered"] == [], r["clustered"]
    assert all(v == "single" for v in r["verdict"].values())


def test_empty_video_and_no_complaints():
    videos = [
        {"video_id": "v1", "comments": []},
        {"video_id": "v2", "comments": [c(), c()]},
    ]
    r = cluster_videos(videos)
    assert r["complaint_rate"] == {"v1": (0, 0), "v2": (0, 2)}
    assert r["clustered"] == []


def test_replies_excluded_from_examined():
    # Only top-level (parent == "root") comments are examined by default.
    videos = [{"video_id": "v1", "comments": [
        {"text": "top", "categories": ["battery"], "parent": "root"},
        {"text": "reply", "categories": ["price"], "parent": "some-id"},
    ]}]
    r = cluster_videos(videos)
    assert r["per_video"]["v1"]["battery"] == 1
    assert r["per_video"]["v1"]["price"] == 0
    assert r["complaint_rate"]["v1"] == (1, 1)


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items())
             if k.startswith("test_")]
    for t in tests:
        t()
        print(f"PASS {t.__name__}")
    print(f"{len(tests)} tests passed")
