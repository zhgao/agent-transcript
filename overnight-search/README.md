# Overnight draft: YouTube search for agents (FREE, $0)

Why: in the best-evidenced x402 seller report found overnight (ScrapeMole,
dev.to), agents paid for YouTube search 16 times out of 18 paid calls, at
$0.005–$0.01, while transcript was bought once. George's live API sells
transcript only. Search is the missing, already-demanded sibling, and it
costs $0 to build: yt-dlp ytsearch, no YouTube Data API key.

Status: LOCAL DRAFT ONLY. Not deployed, not listed, not posted.
Deploying it (e.g. adding it to agent-transcript on Fly) needs George awake
for a Fly token, and any paid version needs his $0.01-test decision.
Do NOT copy this into the Transcriptly app.

Run locally:
  ~/workspace/agent-sales-exploration/.venv/bin/uvicorn app.main:app --port 8769
  curl "http://127.0.0.1:8769/agent/v1/youtube-search?q=Rick+Astley&max_results=5"
