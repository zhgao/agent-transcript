# Verifiable Citation API — local prototype

Idea (2026-11-01 daily idea): an agent asks a question about a video and
gets back the single best timestamped verbatim quote answering it, plus the
video link and start time, plus a confidence note.

## What it does

`citation_api.py` — `find_citation(segments, question, video_url=None)` and
`score_segment(question, segment_text)`.

- Scoring prefers segments sharing the most question keywords
  (2 points per distinct keyword + 1 per extra occurrence), with a +10 bonus
  when the question's exact phrase appears verbatim in the segment.
- Output: the single best quote as `{"question", "video_url", "start", "end",
  "quote", "score", "matched_keywords", "exact_phrase", "confidence"}`.
- Confidence note is honest about match type: "exact phrase match" vs
  "keyword overlap: n/m question keywords appear…" — it does **not** claim
  the quote is true or fully answers the question.
- No match → `None`, not an error. Empty question → `ValueError`.

## Tests

`python3 test_citation_api.py` — **16/16 mock checks pass**
(synthetic segments only; covers best-quote selection, verbatim quote,
both confidence notes, keyword-count preference, exact-phrase bonus,
no-match, empty question, `video_url`/start echo, case-insensitivity,
empty-segment skip, stopword dropping).

## Live accuracy self-test (2026-11-07, via `app/free_transcript.py`)

Attempted on 5 well-known subtitled public videos. **1 of 5 fetched; 4 of 5
blocked.** No results were fabricated — failures are recorded as failures.

| Video | Fetch | Citation result |
|---|---|---|
| Rick Astley — Never Gonna Give You Up (`dQw4w9WgXcQ`) | OK — `captions_api`, 61 segments | Q "what does he promise never to do" → start 128.48, quote "♪ Never gonna give, never gonna give ♪", confidence: keyword overlap 1/2. **PARTIAL**: the quote is a real lyric line in the right spirit, but "promise" never appears in the lyrics, so this is keyword overlap, not a clean answer. The confidence note correctly flags that. |
| Me at the zoo (`jNQXAC9IVRw`) | FAIL | not tested — no transcript |
| PSY — Gangnam Style (`9bZkp7q19f0`) | FAIL | not tested — no transcript |
| Big Buck Bunny (`aqz-KE-bpKQ`) | FAIL | not tested — no transcript |
| Charlie bit my finger (`_OBlgSz8sSM`) | FAIL | not tested — no transcript |

**Blocker (explicit):** the sandbox YouTube IP is blocked by
`youtube-transcript-api` ("YouTube is blocking requests from your IP …
cloud provider"), and the `yt-dlp` fallback fails with
`SSL: CERTIFICATE_VERIFY_FAILED: self-signed certificate` — the sandbox
egress proxy MITMs TLS and yt-dlp does not trust its CA. Rick Astley
happened to succeed through the captions API on both attempts; the other
four failed on both attempts. No proxy, cookies, or paid workaround was
used (that would break the $0 / no-new-accounts constraints).

## Live re-test with the yt-dlp no-certifi fix (2026-11-07, follow-up)

The earlier failures turned out to be partly a sandbox CA problem, not a
YouTube block: yt-dlp defaults to certifi's CA bundle, which lacks the
Hatch egress CA. Using `compat_opts={"no-certifi"}` (system trust store,
which honours `SSL_CERT_FILE`) the caption tracks fetched. Reproducible
via `../live_caption_test.py` (run with the project venv python).
Re-test of the same 5 videos: **2 of 5 fetched**.
- Rick Astley (`dQw4w9WgXcQ`): 61 segments; citation as above (partial).
- Me at the zoo (`jNQXAC9IVRw`): 6 segments; Q "what does he say about
  the elephants" → start 1.20, quote "All right, so here we are, in
  front of the elephants" — the right line, flagged as keyword overlap
  (1/2 keywords) by the confidence note. **Good answer.**
- Gangnam Style (`9bZkp7q19f0`): FAIL — HTTP 429 Too Many Requests.
- Big Buck Bunny (`aqz-KE-bpKQ`): FAIL — no English caption track at all
  (consistent with the known `no_captions` result for this video).
- Charlie bit my finger (`_OBlgSz8sSM`): FAIL — YouTube bot check
  ("Sign in to confirm you're not a bot"); no cookies used, per the $0 /
  no-accounts constraint.

So on the 2 videos that fetched, the citation was sensible both times
(1 partial, 1 good). Fetch reliability, not citation quality, is the
weak link: 429s and bot checks are per-IP and transient. No proxy,
cookies, or paid workaround was used.

## Honest limits

- Local prototype only. Not deployed, not priced, no buyer demand proven.
- Live accuracy is **thin but no longer unproven**: 2 fetched videos, both
  returned a sensible quote; 3 of 5 videos could not be fetched at all.
  The confidence note is the safeguard — it never overclaims.
- $0 spent. No paid services, no accounts, no posting.
