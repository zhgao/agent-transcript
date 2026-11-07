---
description: YouTube search and transcript API for AI agents — free search and free caption transcripts, plus paid search at $0.005/call and paid transcript at $0.01/call in USDC on Base via x402. No account, no API key.
---

# agent-transcript

Base URL: https://agent-transcript.fly.dev

Give a YouTube URL, get a structured transcript back as JSON:
full text plus timed segments. No account, no API key, no signup.

## When to use this skill

Use it when an agent needs to read what a YouTube video actually says —
for research, summarising, fact-checking against a video, or finding
where in a video something was said — without downloading the video.

## Endpoints

### GET /agent/v1/youtube-search

Free YouTube search. No payment, no API key.

- Query: `q=<query>&max_results=5`
- Returns: structured video results as JSON, `cost_usd: 0`.
- Example: `GET https://agent-transcript.fly.dev/agent/v1/youtube-search?q=Rick+Astley&max_results=3`

### GET /agent/v1/transcript

Free transcript from a video's own captions. No payment, no API key.

- Query: `url=<YouTube URL>&lang=auto|en|zh`
- Returns: JSON with `video_id`, `transcript`, `segments[{start, end, text}]`, `source`, `cost_usd`.
- Free caption tiers only.

### GET /agent/v1/youtube-search-paid

Paid YouTube search, $0.005 per call, USDC on Base via x402.
Live-confirmed 2026-10-28 19:32 Beijing: a bare request returns the
x402 payment-required challenge (x402Version 1, scheme exact, network
eip155:8453, maxAmountRequired 5000, Base USDC asset) — not a Not Found.
Pay and retry with the payment header to get search results.
The pay-to address is read from the live 402 at call time and is
deliberately not hard-coded in this skill file.

### GET /agent/v1/transcript-paid

Paid transcript, $0.01 per call, USDC on Base via x402.

- Query: `url=<YouTube URL>&lang=auto|en|zh`
- Without payment it returns HTTP 402 with payment requirements.
- Pay in USDC on Base, retry with the `X-PAYMENT` header, get the transcript.
- Discovery: `/llms.txt`, `/.well-known/agent.json`, `/.well-known/x402`,
  `/x402.json`, `/openapi.json`, `/health`.

## Payment

- Rail: x402, USDC on Base (network `eip155:8453`).
- Paid search: $0.005 per call. Paid transcript: $0.01 per call.
  Free search and free transcript: $0.
- Buyers pay the seller wallet directly; no account or API key is issued.
- Honest limit, do not remove: a real $0.01 payment through a facilitator
  has not yet been settled and verified, and this skill is not listed as
  settlement-verified on any x402 directory. Do not claim otherwise.

## Errors

- Video with no captions: `error=no_captions`, HTTP 404.
  The free endpoint never silently falls back to a paid service.
- Paid endpoint without payment: HTTP 402 with payment requirements.
- Bad payment header on a paid endpoint: HTTP 402, no transcript returned.

## Free routes (liveness)

- `GET /health` — free, no payment, no auth.
- `GET /agent/v1/youtube-search` — free.
- `GET /agent/v1/transcript` — free (caption tiers only).

## What this skill does NOT include

- No MCP wrapper: this is a plain HTTP API skill, not an MCP server.
  MCP directories (Smithery, Glama, official MCP Registry) are a separate
  line and would need an MCP wrapper first.
- The pay-to wallet address is not hard-coded here; agents read it from
  the live 402 challenge at call time, as the public API already does.
