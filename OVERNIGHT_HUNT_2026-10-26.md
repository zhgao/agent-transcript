# Overnight earning hunt — 2026-10-26 (George asleep, $0 budget)

Scope: search X/YouTube/public web for what small builders and AI agents
actually pay for, with $0 to spend. No posting, no DMs, no new accounts,
no spending, no wallet seed/private key touched. All earnings belong to George.

## (a) 3–5 ideas found, with honest evidence ratings

### 1. x402 YouTube search sold to AI agents — EVIDENCE: STRONG (small sample)
- Source: https://dev.to/scrapemole/what-ai-agents-actually-paid-for-in-our-first-day-of-selling-x402-apis-0175-18-calls-2-wallets-28ca
- Claim, self-reported with Cloudflare logs + public Base chain cited:
  $0.175 USDC, 18 paid calls, 2 wallets (neither the seller's), in ~20h.
  What sold: YouTube search 16×, YouTube channel lookup 1×, YouTube
  transcript 1×, all at $0.005–$0.01. Lesson stated: being listed early
  on x402scan / x402dash / Agent402 / 402 Index mattered more than the
  product itself; the 25 newer endpoints had zero sales yet.
- Discount: one seller, one day, $0.175 total. It proves the loop works,
  not that it scales. Still the ONLY idea here with a named product,
  a price, a payer count, and a per-product sales split.

### 2. x402 bundled "intelligence" APIs at $0.10–$0.15 — EVIDENCE: WEAK
- Source: https://dev.to/8randonpickart5/i-built-8-apis-that-ai-agents-pay-for-automatically-2m4o
- 8 endpoints (domain shield, company X-ray, threat pulse, etc.) at
  $0.10–$0.15, built on premium upstream data (VirusTotal, People Data
  Labs, Hunter.io, etc.). No sales, revenue, or payer numbers shown in
  the piece. Upstream costs are real and unpriced in the claim, so the
  margin story is unproven. Not $0-replicable: the upstream APIs are
  the product, and they are not free.

### 3. Apify pay-per-event micro-actors at $0.002–$0.005 — EVIDENCE: MEDIUM (model), WEAK (earnings)
- Sources:
  - https://dev.to/weeknds/how-i-built-7-apify-actors-and-started-earning-passive-income-from-web-scraping-5b9e
  - https://dev.to/jeffreyturov/i-built-11-pay-per-use-data-apis-that-ai-agents-can-call-directly-google-maps-tiktok-linkedin-24b9
- Model is real: Apify takes 20%, PAY_PER_EVENT is the current model
  (rentals retired 2026-10-01). The $100–$150/month figure for 7 actors
  is a PROJECTION (1,000 runs/actor/month), not receipts.
- Trap, from the second source, with numbers: a $0.005/business actor
  earned $0.08 on a 16-business run and paid $1.23 in Playwright +
  residential-proxy compute — margin −1436%. Fix offered: a flat
  run-started event covering fixed cost. Any browser-based actor that
  skips this can lose money on every sale. George's existing Apify
  scaffold (transcript, no browser, no proxy) avoids that trap, which
  is why it stays viable; it is still unpublished (account + pricing
  decisions pending with George).

### 4. Human transcript credit packs + MCP access — EVIDENCE: MEDIUM (pricing), WEAK (revenue)
- Sources: https://ytbulktranscript.app/ , https://api.scripthaul.com/
- Real published prices: bulk transcript as low as $0.01/video (500
  credits $5.99) and $0.02/video via API/MCP; ScriptHaul gives 100 free
  credits/month. No revenue, user count, or conversion numbers shown.
  The market is crowded (multiple free transcript tools), and the
  price floor is already at a cent — a race to the bottom, not a
  margin story. Useful as a price anchor for George's $0.01/call, not
  as proof of demand.

### 5. "Sell AI agent systems for $500/month per client" — EVIDENCE: WEAK (hype discount)
- Source: https://youtubetotranscript.com/transcript?v=t6NxHM5peus (transcript of a YouTube tutorial)
- Claim: build an agent system with Claude Code + a platform, sell one
  client at $500/month and the stack pays for itself (50 client slots
  on the agency plan). No verified client, contract, or payment shown;
  the video funnels to a paid course. The $500 is an asking price, not
  a sale. Requires human sales, onboarding, and support — the opposite
  of a $0 overnight build.

### Sobering base rate (context, not an idea)
- https://www.scoutr.dev/blog/indie-startup-revenue-report — 8,817
  startups: 54% make exactly $0; developer tools worst at 69% at $0
  and only 6.5% above $1k/month. "Useful" and "paid for" are different
  problems, and George's category (dev tools / agent APIs) is the
  hardest one in that dataset.

## (b) The ONE chosen idea — and why

**Add YouTube search to the agent-transcript offer, as a free endpoint
first, paid x402 version only after George's price/test decision.**

Why this one and not the others:
- It is the exact thing agents demonstrably paid for (idea 1: 16 of
  18 paid calls), while George's live API currently sells only the
  thing they bought once (transcript). Search is the missing sibling.
- It costs $0: yt-dlp ytsearch, no YouTube Data API key, no paid
  upstream, no browser, no proxy — so it cannot repeat the Apify
  compute-loss trap (idea 3).
- It extends an already-live, already-posted product instead of
  starting a new brand, audience, or sales motion from zero.

## (c) What was actually built and its local test result

New SEPARATE codebase (nothing in the live agent-transcript app and
nothing in the human-facing Transcriptly app was touched):
- `~/workspace/agent-sales-exploration/overnight-search/`
  - `app/youtube_search.py` — yt-dlp ytsearch primary, plus a
    public-search-page fallback (ytInitialData parsing) used only
    when yt-dlp fails.
  - `app/main.py` — FastAPI: `GET /health`,
    `GET /agent/v1/youtube-search?q=&max_results=` (1–10, default 5).
  - `README.md` — status: LOCAL DRAFT ONLY, and the deploy steps it
    deliberately does NOT take.

Local test results (port 8769, test server stopped afterwards):
- `/health` → 200 `{"status":"ok","service":"youtube-search","cost_per_call_usd":0}` — PASS
- `?q=Rick+Astley&max_results=5` → 5 results, each with video_id,
  title, url, channel, duration_seconds, view_count — PASS
  (e.g. "Rick Astley - Never Gonna Give You Up (Official Music Video)
  (1987)", 213s). Note: search ranking varies; the canonical
  dQw4w9WgXcQ was not the first hit, which is YouTube's ranking,
  not a bug.
- `?q=x402+AI+agents&max_results=3` → 3 results, including a Fireship
  x402 video — PASS
- `?q=` → 400 `{"error":"query is required"}` — PASS
- Known sandbox quirk, honestly recorded: yt-dlp's search path fails
  in this sandbox on the egress proxy's MITM CA even with a CA-bundle
  override; the HTML fallback is what passed locally. On Fly (normal
  CA, no MITM proxy) yt-dlp should work, but that must be re-tested
  after deploy — do NOT claim production search works until then.
  The fallback is test-only evidence, not a production guarantee.

## (d) What is still blocked and what it needs

1. Public deploy: needs George awake to paste a Fly token once
   (use-once rule; no token is stored anywhere by this hunt).
   Suggested deploy: add this search endpoint alongside the live
   agent-transcript app, keeping the free transcript untouched.
2. Paid version: needs George's decision on price ($0.005 to match
   the ScrapeMole evidence, vs the existing $0.01) and on the real
   $0.01 self-test he previously deferred ("no recharge, wait for a
   real buyer").
3. Discovery/listing: no directory submission was made, no post was
   published, no account was created. The ScrapeMole lesson says
   listing early is the lever — that is the first post-wake action
   to approve, not something done silently overnight.
4. Apify track: unchanged — still blocked on George's Apify account
   email choice and final pricing confirmation.

## (e) Earnings so far

- Revenue: **$0** (no verifiable payment evidence; none invented).
- Spend: **$0** (no paid API, no paid listing, no paid deploy).
- Net: **$0**. The live agent-transcript API remains the only
  revenue surface, and it has no verified paid call yet.
