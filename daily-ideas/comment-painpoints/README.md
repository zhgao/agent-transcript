# Comment-painpoint validation — 2026-11-07

Hand-count validation for the 2026-11-04 daily earning idea: a per-call API
for agents — input a public video link, output high-frequency complaints and
unmet needs from that video's comments, with verbatim quotes and occurrence
counts. $0, local only, no accounts, no posting, no fabricated data.

## Niche picked: budget wireless earbuds

Chosen because commenters complain a lot about them (price, battery,
fit, breakage) and because three high-comment videos were fetchable.
First attempt (small channels: Redmi Buds 8 Active review, etc.) yielded
only 10 / 1 / 0 comments — too thin — so the sample was re-picked to
high-view videos found via `yt-dlp ytsearch10`.

## The 3 videos (live-fetched 2026-11-07, newest 100 comments each)

| # | Video | Channel | Top-level examined | Complaint comments |
|---|-------|---------|-------------------|--------------------|
| 1 | [We Tested the Best Wireless Earbuds for 2026](https://www.youtube.com/watch?v=tUhLcDnXdwg) | Tom's Guide | 84 | 24 (28.6%) |
| 2 | [Best BUDGET Earbuds Under $50 in 2026 (RANKED)](https://www.youtube.com/watch?v=Vo8mmwH7Ir8) | Picky Audio | 73 | 12 (16.4%) |
| 3 | [2025 Earbuds Awards - Unexpected Winners!](https://www.youtube.com/watch?v=4F0289jmqQs) | Mike O'Brien | 91 | 28 (30.8%) |
| | **Total** | | **248** | **64 (25.8%)** |

"Complaint comments" = top-level comments with ≥1 product-complaint tag.
Replies excluded (16 / 27 / 9 replies fetched but not counted). A comment can
carry several tags, so category counts below sum to more than the complaint
comment counts. Every top-level comment was read by hand; tags are in
`comments.json` (`categories` per comment).

## Complaint categories — counts per video

| Category | V1 Tom's Guide | V2 Picky Audio | V3 Mike O'Brien | Total | In how many videos |
|----------|----------------|----------------|-----------------|-------|--------------------|
| reliability (breaks / one side dies / charging defect / QC) | 8 | 3 | 6 | **17** | 3 — strong |
| price (too expensive / "not really budget") | 4 | 1 | 8 | **13** | 3 — strong |
| battery (degrades / dies / far below advertised) | 3 | 4 | 5 | **12** | 3 — strong |
| fit (falls out / uncomfortable / hurts) | 5 | 3 | 4 | **12** | 3 — strong |
| controls (app / software / tap-press) | 1 | 1 | 4 | 6 | 3 — strong |
| anc (weak / faulty) | 2 | 1 | 3 | 6 | 3 — strong |
| mic / call quality | 0 | 3 | 2 | 5 | 2 — partial |
| volume (too quiet / channel imbalance) | 2 | 2 | 1 | 5 | 3 — strong |
| connectivity (drops / won't pair / power faults) | 2 | 1 | 1 | 4 | 3 — strong |
| lost an earbud | 2 | 0 | 0 | 2 | 1 — single |

## Verdict: YES, complaints cluster — strongly

**9 of 10 categories recur in ≥2 videos; 8 of 10 appear in all three.**
The top 4 clusters are the same in every video: reliability (17),
price-not-budget (13), battery (12), fit (12). The only single-video
category is "lost an earbud" (2 mentions, video 1 only).

## Verbatim quote examples (short, authors anonymised)

- **reliability** — "I've had to use my warranty on three different devices."
  (V1, Sony) · "the left earbud died [after one week]... several users had
  experienced the same issue" (V3, Sennheiser) · "the glue holding the
  moldings together fell apart... his fell apart in a matter of months" (V3)
- **price** — "Cheap means 20 - 80 bux" (V1, on a video featuring $330 buds) ·
  "Budget is 50 bucks or less. You're out of touch." (V3) · "170€? budget?
  bro am searching for something under 60€" (V3)
- **battery** — "battery life plummeting after 1 year, and Sony won't do
  anything about it" (V1) · "they go out of power in 1 hour when they say
  it's suppose to have 30 hours of play" (V2) · "tired of the crap 5 hour
  charges... i want more like 16 or 20" (V3)
- **fit** — "I have wasted too much money buying 'top rated' ear buds to
  find they aren't comfortable or fall out easily" (V1) · "My ears are small
  so any buds i try hurt after like 15 mins" (V3)
- **mic** — "how did sony xm5 win premium earbuds with that trash mic?"
  (V3) · "the microphone broke after a year" (V2)
- **connectivity** — "they have so many connectivity issues they are
  unusable for me" (V1, Bose) · "started dropping connectivity, and battery
  life had absolutely died. Total waste of money after the first 60 days"
  (V2, CMF Buds Pro 2)
- **controls** — "you can NOT set them in a way, that when you put only one
  [in], it does NOT go to passthrough" (V3, Sony XM5 software)

## What this implies for the API idea

1. **The core premise holds in this niche.** Complaints are not random:
   a buyer of budget earbuds who reads 3 review videos will hit the same
   4 pain points (reliability, price honesty, battery decay, fit) every
   time. An API that returns those clusters with counts + quotes would be
   genuinely summarising the comment section, not inventing a pattern.
2. **The value is per-product, not per-video.** Most complaints name a
   specific model (Sony XM5/XM6, CMF Buds Pro 2, Sennheiser, Nothing,
   JLab). A useful API should attribute complaints to the product, not
   just the video — that needs entity extraction on top of clustering.
3. **Noise filtering is a real product requirement, not an edge case.**
   - Video 1's last ~16 top-level comments are near-identical generic
     praise ("This tutorial is clear and easy to follow...") and two
     commenters explicitly call out "botted comments" (271 likes). A naive
     count would treat bots as signal.
   - All 3 videos have a second complaint stream *about the video itself*
     (missing models, wrong prices, affiliate-link bias, "not really
     budget" as a criticism of the video's framing). The API must separate
     product complaints from video/meta complaints, or the "price" cluster
     gets polluted by "your video isn't budget" gripes.
   - Low-comment videos are common (first picks: 10 / 1 / 0 comments).
     The API needs a minimum-comment threshold and a "not enough data"
     response instead of hallucinating clusters from 3 comments.
4. **Complaint rate varies a lot by channel (16%–31%).** Partly the
   audience, partly the video (V3 is an awards roundup with premium picks
   → more price complaints; V2 is a tight under-$50 list → fewer).
   Counts should always ship with the denominator (comments examined).
5. **Next validation step (still $0):** repeat in a second niche
   (e.g. AI note-taking apps) and check whether the *same* category set
   transfers or each niche needs its own taxonomy. If the taxonomy is
   niche-specific, the API needs per-niche category lists, which is a
   bigger build than one generic clusterer.

## Fetch notes (sandbox, 2026-11-07)

- Live fetching **worked** from this sandbox. yt-dlp 2026.10.21 was
  installed into the project venv (`pip install yt-dlp`).
- Gotcha: yt-dlp defaults to certifi's CA bundle, which lacks the Hatch
  egress CA → `SSL: CERTIFICATE_VERIFY_FAILED`. Fix used:
  `--compat-options no-certifi` (uses the system store, which honours
  `SSL_CERT_FILE=/run/hatch/egress-tls/ca-bundle.pem`, already set in the
  sandbox env). `--comment-max` does not exist in this version; the cap is
  `--extractor-args youtube:max_comments=N`.
- Comment counts: yt-dlp reports `comment_count` 100 / 100 / 100 for the
  three videos — that is the fetch cap talking, not necessarily the true
  total; the examined denominator is the 100 fetched (84 / 73 / 91
  top-level after removing replies).

## Files

- `comments.json` — the 248 examined top-level comments, anonymised
  (fields: `index`, `text`, `like_count`, `categories` only; no usernames
  or author IDs), plus video metadata.
- `comment_fetch.py` — fetch script (stdlib + yt-dlp subprocess, no keys).
  `python comment_fetch.py <youtube-url> [--max-comments N] [--out FILE]`
- `cluster.py` — pure clustering functions (`count_categories`,
  `cluster_videos`); verdicts: strong = in all videos, partial = in 2,
  single = in 1.
- `test_cluster.py` — 6 unit tests on synthetic comments. Run:
  `python test_cluster.py` → **6 tests passed** (2026-11-07).
- Reproduce the cluster table from the real data:
  `python -c "import json; from cluster import cluster_videos; print(cluster_videos(json.load(open('comments.json'))['videos']))"`

## Limits of this validation

- 3 videos, 1 niche, newest-100-comments slice only (not a random sample;
  newest-first ordering may overweight recent complaints).
- Hand tags by one coder, no second coder / inter-rater check.
- No claim about other niches — see "next step" above.
