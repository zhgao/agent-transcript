# Daily earning-report ideas — implementation report (2026-11-07)

George confirmed 2026-11-07: implement ALL ideas from the daily earning
reports (2026-10-26 → 2026-11-07), not just report them. This file is the
consolidated status. Everything below is **local only** unless stated
otherwise: $0 spent, no paid services, no Deepgram, no new accounts, no
public posting, no deployment to Fly, no wallet/seed/private keys.
Revenue remains $0 (LEDGER.md unchanged); nothing here is a claim of buyer
demand — demand for every idea is still unproven.

## Summary

| # | Idea (report date) | Built? | Tests | Ready locally? | Blocked by |
|---|---|---|---|---|---|
| 1 | Free + paid YouTube search (2026-10-26) | Yes — `app/youtube_search.py`, paid endpoint in `app/main.py` | Mock-tested 2026-10-26; free endpoint live on Fly since 2026-10-26 | Free: live. Paid $0.005: local only | Deploy needs a fresh Fly token from George; real-payment test needs his "wait for a real buyer" decision to change |
| 2 | Video keyword locator (2026-10-26) | Yes — `keyword-locator/` | 8/8 mock, re-run 2026-11-07 | Yes | Wiring to free transcript layer / pricing: George's call |
| 3 | On-chain read-only endpoints (2026-10-27) | Yes — `chain-readonly/` | 19/19 mock, re-run 2026-11-07 | Yes (mock only) | Live latency never measured (background-run policy); pricing/deploy: George's call |
| 4 | Video assertion-evidence locator (2026-10-28) | **Yes, new 2026-11-07** — `daily-ideas/assertion-evidence/` | 14/14 mock | Yes | Not deployed, not priced; matching is substring-based — it finds where terms are spoken, not whether the assertion is true |
| 5 | GitHub public-repo quick-read (2026-10-29) | Yes — `repo-quickread/` | 19/19 mock, re-run 2026-11-07 | Yes | No live GitHub fetch wired; pricing/deploy: George's call |
| 6 | MCP server wrapper, free search only (2026-10-30) | Yes — `mcp-server/` | 11/11 protocol, re-run 2026-11-07; **Inspector CLI check done 2026-11-07** (tools/list + tools/call round-trip) | Yes (protocol) | Live search through Inspector fails in the sandbox (proxy SSL); needs a non-sandbox run for end-to-end. Directory submission needs George's go-ahead |
| 7 | URL → clean Markdown (2026-10-31) | Yes — `url-markdown/` | 3/3 live pages, re-run 2026-11-07 | Yes | Long pages come out huge (~330k chars for Wikipedia) — needs a length cap before any paid version |
| 8 | Verifiable citation API (2026-11-01) | **Yes, new 2026-11-07** — `daily-ideas/citation-api/` | 16/16 mock; live re-test: 2/5 videos fetched, both returned a sensible quote (1 partial, 1 good) | Yes | Fetch reliability: 429 / no captions / bot check on 3 of 5 videos; not deployed, not priced |
| 9 | Apify PAY_PER_EVENT publish check (2026-11-02) | Yes — `apify-actor/` scaffold (pre-existing) | **Re-run 2026-11-07: exit 0**, Rick Astley 2,089 chars / 61 segments, `charged=true`, event `transcript-delivered` | Yes locally | Publishing needs an Apify account + George's approval + pricing confirmation ($0.05 draft) |
| 10 | Key-point timestamp search (2026-11-03) | **Yes, new 2026-11-07** — `daily-ideas/keypoint-search/` | 16/16 mock; live re-test: 2/5 videos fetched, both topics PASS | Yes | Same fetch limits as #8; not deployed, not priced |
| 11 | Public video comment pain-point mining (2026-11-04) | **Yes, new 2026-11-07** — `daily-ideas/comment-painpoints/` | 6/6 cluster unit tests; **live validation: 3 videos, 248 top-level comments hand-tagged** | Yes — validation done | See findings below; needs a 2nd niche to check taxonomy transfer |
| 12 | Public trends summary /v1/trends (2026-11-06) | Yes — `trends-summary/` | 24/24 mock, re-run 2026-11-07; **HN upstream verified live 2026-11-07** (500 story IDs, no key) | Yes | Not wired into the FastAPI app as a free endpoint yet; GitHub trending has no official API (HN only) |
| 13 | Public RSS summary API (2026-11-07) | Yes — `rss-summary/` | 19/19 mock, re-run 2026-11-07; live feeds verified (GitHub Blog, hnrss) | Yes | HN items' descriptions are link text, not prose — needs a per-source rule before charging for HN feeds |

2026-11-05 had no new idea (report said so explicitly); it re-used #11.

## What was new on 2026-11-07

- `daily-ideas/assertion-evidence/` — `locate_assertion()` with key-term
  scoring + exact-phrase bonus, ranked matches. 14/14 mock checks.
- `daily-ideas/citation-api/` — `find_citation()` returning the single
  best timestamped verbatim quote + honest confidence note. 16/16 mock.
- `daily-ideas/keypoint-search/` — topic-level timestamp search with a
  per-hit summary line. 16/16 mock.
- `daily-ideas/comment-painpoints/` — live validation (see below).
- `daily-ideas/live_caption_test.py` — reproducible live-caption fetcher
  used for the #8/#10 re-tests.

## Key findings from the live checks (2026-11-07)

1. **Comment complaints DO cluster (niche: budget wireless earbuds).**
   3 videos, 248 top-level comments hand-read, 64 complaint comments
   (25.8%). 9 of 10 categories recur in ≥2 videos; 8 of 10 in all three.
   Top clusters: reliability (17), price-not-budget (13), battery (12),
   fit (12). Caveats found by the validation itself: bot-like praise
   comments pollute counts; complaints split between the product and the
   video itself; low-comment videos are common (first picks had 10/1/0
   comments) so the API needs a minimum-comment threshold. Next step:
   repeat in a second niche to check whether the taxonomy transfers.
2. **The sandbox YouTube caption block is partly a CA problem, not an IP
   block.** yt-dlp with `compat_opts={"no-certifi"}` (system trust store)
   fetches caption tracks through the egress proxy; the plain
   youtube-transcript-api tier stays IP-blocked. With the fix, 2 of 5
   test videos fetched (Rick Astley 61 segments; Me at the zoo 6);
   Gangnam Style hit HTTP 429, Big Buck Bunny has no English captions,
   Charlie bit my finger hit a bot check. Citation: 2/2 sensible quotes
   (1 partial, 1 good). Key-point: 2/2 PASS. Fetch reliability, not
   matching quality, is the weak link.
3. **MCP Inspector protocol verified.** Inspector CLI v2.13.0 (npx cache)
   `tools/list` returned exactly the one `youtube_search` tool and a
   `tools/call` round-tripped. Live search through Inspector fails only
   in the sandbox (proxy SSL); the same code returns real results when
   run directly. Note: run the server with the project venv python —
   system `python3` lacks yt-dlp, so the server falls back to its
   "backend unavailable" stub.
4. **Apify scaffold re-verified.** Fresh local run 2026-11-07, exit 0,
   Rick Astley transcript 2,089 chars / 61 segments via `captions_api`,
   `charged=true`, event `transcript-delivered`. The local-mode "ignored
   charge attempt" warning is expected (no pay-per-event pricing in
   local mode) and confirms the charge-before-push ordering is in code.
5. **HN upstream is live.** `topstories.json` returned 500 story IDs,
   no key needed.

## What is still blocked (all need George)

- **Deploy anything to Fly** (paid search $0.005, trends endpoint, any
  new prototype): needs George to paste a fresh Fly token; the 2026-10-26
  token was consumed by the free-search deploy.
- **Real x402 payment test** ($0.01 transcript / $0.005 search): needs
  either a funded wallet (~$1–2 Base USDC + a little Base ETH) or a real
  external buyer; George's standing decision is "wait for a real buyer,
  do not recharge."
- **Apify publish**: no Apify account exists; signup email
  (zhgao@foxmail.com vs zhgao1981@gmail.com) unanswered; final pricing
  ($0.05/transcript-delivered draft) unconfirmed.
- **Pricing for every new prototype**: none of #4, #8, #10, #11, #12,
  #13 has a decided price. $0.005 was floated for several; it is not a
  decision.
- **MCP directory submission** (Smithery/Glama/Registry): prototype
  removes the blocker, submission itself still needs his go-ahead.
- **Chain read-only live latency**: still unmeasured; needs a normal
  (non-background) run against the public Base RPC.

## Suggested next step (one thing, $0)

Apply the yt-dlp `no-certifi` fix to `app/free_transcript.py` (one-line
compat option, sandbox-only effect in practice) and re-run the live
transcript check for the 5 test videos — if that unblocks the free
transcript layer in the sandbox, the citation/key-point live accuracy
can be measured on more videos without touching Fly. This is a code
change to shared code, so it should be done as its own small, tested
step, not silently inside this report.

## Files

- This report: `daily-ideas/IMPLEMENTATION_REPORT.md`
- New prototypes: `daily-ideas/assertion-evidence/`,
  `daily-ideas/citation-api/`, `daily-ideas/keypoint-search/`,
  `daily-ideas/comment-painpoints/` (incl. `comments.json`, 248
  anonymised comments), `daily-ideas/live_caption_test.py`
- Pre-existing prototypes (re-verified 2026-11-07, tests re-run):
  `keyword-locator/`, `chain-readonly/`, `repo-quickread/`,
  `mcp-server/`, `url-markdown/`, `trends-summary/`, `rss-summary/`,
  `apify-actor/`, `app/` (paid search endpoint, local only)
