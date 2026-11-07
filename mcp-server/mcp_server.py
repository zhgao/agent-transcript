"""Minimal MCP server for agent-transcript, stdlib only, free search only.

Deliberate scope limit, by design:
- Exposes exactly ONE tool: youtube_search (the free endpoint's logic).
- No paid endpoints (no youtube-search-paid, no transcript-paid), no wallet,
  no signing, no payment header handling anywhere in this file.
- Speaks MCP over stdio as plain JSON-RPC 2.0 (newline-delimited), so no
  `mcp` SDK install is needed. Protocol surface implemented:
  initialize -> tools/list -> tools/call, plus ping and notifications/*.
- The search implementation is imported from app/youtube_search.py when
  available; tests monkeypatch `search_youtube` so protocol tests never
  touch the network.

Run:  python3 mcp_server.py   (reads JSON-RPC lines on stdin, writes on stdout)
"""
import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

try:
    from app.youtube_search import search_youtube
except Exception:  # pragma: no cover - import fallback for direct runs
    def search_youtube(query, max_results=5):
        raise RuntimeError("youtube_search backend unavailable")

PROTOCOL_VERSION = "2024-11-05"
SERVER_INFO = {"name": "agent-transcript", "version": "0.1.0"}

TOOL = {
    "name": "youtube_search",
    "description": (
        "Search YouTube for videos matching a query. Free, no API key, "
        "no account. Returns structured results (video_id, title, url, "
        "channel, duration_seconds) with cost_usd 0. Paid transcript "
        "endpoints are NOT exposed by this server."
    ),
    "inputSchema": {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Search query"},
            "max_results": {"type": "integer", "minimum": 1, "maximum": 10,
                            "default": 5},
        },
        "required": ["query"],
    },
}


def _result(req_id, result):
    return {"jsonrpc": "2.0", "id": req_id, "result": result}


def _error(req_id, code, message):
    return {"jsonrpc": "2.0", "id": req_id,
            "error": {"code": code, "message": message}}


def handle(msg):
    """Handle one JSON-RPC message dict; return a response dict or None."""
    method = msg.get("method")
    req_id = msg.get("id")
    if method is None:
        return None
    if method.startswith("notifications/"):
        return None  # notifications get no response
    if method == "initialize":
        return _result(req_id, {
            "protocolVersion": PROTOCOL_VERSION,
            "capabilities": {"tools": {}},
            "serverInfo": SERVER_INFO,
        })
    if method == "ping":
        return _result(req_id, {})
    if method == "tools/list":
        return _result(req_id, {"tools": [TOOL]})
    if method == "tools/call":
        params = msg.get("params") or {}
        name = params.get("name")
        args = params.get("arguments") or {}
        if name != "youtube_search":
            return _result(req_id, {
                "content": [{"type": "text",
                             "text": f"unknown tool: {name}"}],
                "isError": True})
        try:
            out = search_youtube(args.get("query", ""),
                                 int(args.get("max_results", 5)))
        except Exception as e:
            return _result(req_id, {
                "content": [{"type": "text", "text": f"error: {e}"}],
                "isError": True})
        return _result(req_id, {
            "content": [{"type": "text", "text": json.dumps(out)}]})
    return _error(req_id, -32601, f"method not found: {method}")


def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            sys.stdout.write(json.dumps(
                _error(None, -32700, "parse error")) + "\n")
            sys.stdout.flush()
            continue
        resp = handle(msg)
        if resp is not None:
            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main()
