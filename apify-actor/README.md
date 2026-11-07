# Apify Actor: YouTube Transcript (free captions) — scaffold, NOT published

Status: local scaffold only. No Apify account created, no Actor published,
no pricing activated. Publishing is a public action and needs George's
go-ahead after the Apify account + pricing are confirmed.

## What it does

Input: `videoUrl` (YouTube URL, required), `lang` (`auto|en|zh`).
Output dataset item: `video_id, url, transcript, segments[{start,end,text}], source, cost_usd, charged, charge_event`.
No-caption video: error item with `charged=false`, no charge, no paid fallback
(the paid tier does not exist in this code at all).

## Pricing (draft, set in Console at publish time, not in code)

- Model: PAY_PER_EVENT (Apify requires this for new Actors; PRICE_PER_DATASET_ITEM is rejected)
- Event: `transcript-delivered`, draft $0.05 per delivered transcript
- Charge is called BEFORE `push_data`, inside the handler — otherwise the
  charge can silently vanish when the run closes.
- Apify takes 20%; the developer keeps 80% of event revenue.
- Compute note: this Actor uses no browser/Playwright, only caption APIs,
  so fixed compute is small — unlike browser actors, no separate flat
  `run-started` fee is proposed at this stage. Re-check real compute cost
  on the first paid runs before locking the price.

## Local test (no Apify account needed for a dry run)

Apify SDK local storage: set `APIFY_LOCAL_STORAGE_DIR` and put INPUT.json
under `storage/key_value_stores/default/`, then run the module. The SDK
in local/test mode does not bill. Full local-test commands are in
TEST_REPORT.md for this Actor once the run is done.

## x402 second track (separate, not in this Actor)

The standalone FastAPI agent API (`../app/`) stays as the x402 track.
It stays `payment_enabled=false` until George posts his own Base wallet
public address (0x…). Muse never creates, holds, or stores a seed/private key.
