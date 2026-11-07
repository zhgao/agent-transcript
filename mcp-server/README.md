# agent-transcript MCP server — local prototype only

Stdlib-only MCP server over stdio. Exposes exactly one tool:

- `youtube_search` (query required, max_results 1–10): the free YouTube
  search logic from `../app/youtube_search.py`. Cost $0, no API key.

Deliberately NOT exposed: any paid endpoint, any wallet, any signing.
Nothing here is deployed, no account was created, nothing was spent.

Run: `python3 mcp_server.py` (JSON-RPC lines on stdin/stdout)

Test: `python3 test_mcp_server.py` — 11/11 green (2026-10-31 morning,
Beijing). Tests use a stubbed search function, so they prove the MCP
protocol surface (initialize / tools/list / tools/call / ping /
notifications), NOT a live YouTube lookup and NOT an MCP Inspector run.

## MCP Inspector check (2026-11-07, local, $0)
Inspector CLI v2.13.0 was found in the npx cache
(`~/.npm/_npx/5a9d879542beca3a/node_modules/.bin/mcp-inspector`)
and run in `--cli` mode against this server — protocol verified:
`tools/list` returned exactly the one `youtube_search` tool with its
input schema, and a `tools/call` round-tripped and returned a
structured MCP response. Live search through Inspector did NOT return
results from this sandbox: with system `python3` the server's import
of `app.youtube_search` fails (yt-dlp/requests are only in the project
venv, not system Python) so it fell back to its "backend unavailable"
stub; with the venv python the import worked but the live YouTube call
failed on sandbox egress-proxy SSL errors (yt-dlp SSL errors, then the
HTML fallback also SSL-failed inside the Inspector subprocess). The
same search code run directly in this shell returned real results via
the HTML fallback (Rick Astley canonical video first), so this is a
sandbox-proxy limitation, not a server bug — a live end-to-end check
still needs a non-sandbox run (e.g. on Fly). Run the server with the
project venv python (`../.venv/bin/python mcp_server.py`) when a live
backend is wanted; `python3` is fine for protocol tests only.

Next decisions for George (none urgent, none taken here):
1. Accept the Inspector protocol check as done; live end-to-end still
   needs a non-sandbox run.
2. Whether to submit to MCP directories (Smithery / Glama / official MCP
   Registry) — those were previously blocked precisely because there was
   no MCP wrapper; this prototype removes that blocker, but submission
   itself still needs his go-ahead.
3. Whether paid endpoints ever get an MCP tool — currently no.
