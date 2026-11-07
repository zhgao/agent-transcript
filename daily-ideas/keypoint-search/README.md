# Key-Point Timestamp Search — local prototype

Idea (2026-11-03 daily idea): an agent gives a topic/keyword and a subtitled
public video and gets back the ordered timestamped segments where that topic
is discussed, each with a short summary line.

## What it does

`keypoint_search.py` — `search_keypoints(segments, topic, video_url=None, max_matches=20)`

- Topic-level, not single-keyword: multi-term topics split into key terms
  (stopwords dropped); a segment matches if it contains any term. Ranked by
  distinct terms matched, then total occurrences, then start time.
- Each hit: `{"start", "end", "text", "summary", "score", "matched_terms"}`.
  Summary = first ~120 chars of the segment, cut at a word boundary with
  an ellipsis when truncated; short segments are unchanged.
- No match → empty `matches` list, not an error. Empty topic → `ValueError`.
- Differs from `keyword-locator` (single exact keyword, occurrence counts)
  by supporting multi-term topics, ranking by term coverage, and adding the
  summary line per hit.

## Tests

`python3 test_keypoint_search.py` — **16/16 mock checks pass**
(synthetic segments only; covers ordering, multi-term topics, summary
truncation/ellipsis/prefix, short-summary passthrough, no-match, empty
topic, case-insensitivity, `video_url` echo, `max_matches`,
empty-segment skip, stopword dropping).

## Live accuracy self-test (2026-11-07, via `app/free_transcript.py`)

Attempted on 3 subtitled public videos. **1 of 3 fetched; 2 of 3 blocked.**
No results were fabricated — failures are recorded as failures.

| Video | Fetch | Key-point result |
|---|---|---|
| Rick Astley — Never Gonna Give You Up (`dQw4w9WgXcQ`) | OK — `captions_api`, 61 segments | Topic "never gonna give you up": **20 hits (capped at 20), first at 43.0s — PASS.** The hits are the chorus lines, which is exactly where the topic is sung. |
| Me at the zoo (`jNQXAC9IVRw`) | FAIL | not tested — no transcript |
| PSY — Gangnam Style (`9bZkp7q19f0`) | FAIL | not tested — no transcript |

(The same run also tried Big Buck Bunny and Charlie bit my finger for the
sibling citation prototype; both failed to fetch for the same reason.)

**Blocker (explicit):** the sandbox YouTube IP is blocked by
`youtube-transcript-api` ("YouTube is blocking requests from your IP …
cloud provider"), and the `yt-dlp` fallback fails with
`SSL: CERTIFICATE_VERIFY_FAILED: self-signed certificate` — the sandbox
egress proxy MITMs TLS and yt-dlp does not trust its CA. No proxy, cookies,
or paid workaround was used (that would break the $0 / no-new-accounts
constraints).

## Live re-test with the yt-dlp no-certifi fix (2026-11-07, follow-up)

Same fix as the citation prototype: `compat_opts={"no-certifi"}` lets
yt-dlp fetch caption tracks through the sandbox egress proxy.
Reproducible via `../live_caption_test.py` (project venv python).
Re-test of 5 videos: **2 of 5 fetched**.
- Rick Astley (`dQw4w9WgXcQ`): topic "never gonna give you up" → 20 hits
  (capped), first at 43.0s — PASS.
- Me at the zoo (`jNQXAC9IVRw`): topic "elephants" → 1 hit at 1.20s —
  PASS (the video is 19s long and mentions elephants once).
- Gangnam Style (`9bZkp7q19f0`): FAIL — HTTP 429 Too Many Requests.
- Big Buck Bunny (`aqz-KE-bpKQ`): FAIL — no English caption track at all.
- Charlie bit my finger (`_OBlgSz8sSM`): FAIL — YouTube bot check
  ("Sign in to confirm you're not a bot"); no cookies used.

## Honest limits

- Local prototype only. Not deployed, not priced, no buyer demand proven.
- Live accuracy is **thin**: 2 fetched videos, 2 topics, both passed —
  a smoke signal, not proof. Three of five videos could not be fetched.
- $0 spent. No paid services, no accounts, no posting.
