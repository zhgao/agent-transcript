"""Protocol tests for mcp_server.py. No network: tools/call uses a stub."""
import json, subprocess, sys, os
sys.path.insert(0, os.path.dirname(__file__))
import mcp_server

checks = []
def check(name, cond):
    checks.append((name, bool(cond)))
    print(("PASS" if cond else "FAIL"), name)

# 1. initialize handshake
r = mcp_server.handle({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}})
check("initialize returns protocolVersion + serverInfo",
      r["result"]["protocolVersion"] == "2024-11-05" and r["result"]["serverInfo"]["name"] == "agent-transcript")
# 2. tools/list exposes exactly one tool, free search only
r = mcp_server.handle({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
tools = r["result"]["tools"]
check("tools/list exposes exactly one tool named youtube_search",
      len(tools) == 1 and tools[0]["name"] == "youtube_search")
check("tool requires query, max_results capped at 10",
      tools[0]["inputSchema"]["required"] == ["query"] and tools[0]["inputSchema"]["properties"]["max_results"]["maximum"] == 10)
check("no paid tool exposed", all("paid" not in t["name"] for t in tools))
# 3. notifications get no response
check("notification returns None",
      mcp_server.handle({"jsonrpc": "2.0", "method": "notifications/initialized"}) is None)
# 4. ping
check("ping ok", mcp_server.handle({"jsonrpc": "2.0", "id": 3, "method": "ping"})["result"] == {})
# 5. tools/call with stubbed search
orig = mcp_server.search_youtube
mcp_server.search_youtube = lambda q, n=5: {"query": q, "results": [{"video_id": "dQw4w9WgXcQ", "title": "stub", "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"}], "count": 1, "cost_usd": 0}
r = mcp_server.handle({"jsonrpc": "2.0", "id": 4, "method": "tools/call",
                       "params": {"name": "youtube_search", "arguments": {"query": "Rick Astley", "max_results": 3}}})
body = json.loads(r["result"]["content"][0]["text"])
check("tools/call returns stub result with cost 0", body["count"] == 1 and body["cost_usd"] == 0)
# 6. unknown tool -> isError, not crash
r = mcp_server.handle({"jsonrpc": "2.0", "id": 5, "method": "tools/call",
                       "params": {"name": "transcript-paid", "arguments": {}}})
check("paid/unknown tool rejected with isError", r["result"].get("isError") is True)
# 7. empty query -> isError via stub raising
mcp_server.search_youtube = lambda q, n=5: (_ for _ in ()).throw(ValueError("query is required"))
r = mcp_server.handle({"jsonrpc": "2.0", "id": 6, "method": "tools/call",
                       "params": {"name": "youtube_search", "arguments": {"query": ""}}})
check("empty query returns isError", r["result"].get("isError") is True)
mcp_server.search_youtube = orig
# 8. unknown method -> -32601
r = mcp_server.handle({"jsonrpc": "2.0", "id": 7, "method": "resources/list"})
check("unknown method returns -32601", r["error"]["code"] == -32601)
# 9. stdio smoke: subprocess initialize + tools/list, no network touched
p = subprocess.run([sys.executable, os.path.join(os.path.dirname(__file__), "mcp_server.py")],
                   input='{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}\n{"jsonrpc":"2.0","id":2,"method":"tools/list"}\n',
                   capture_output=True, text=True, timeout=30)
lines = [json.loads(x) for x in p.stdout.strip().splitlines()]
check("stdio subprocess answers initialize + tools/list",
      len(lines) == 2 and lines[1]["result"]["tools"][0]["name"] == "youtube_search")
failed = [n for n, ok in checks if not ok]
print(f"{len(checks)-len(failed)}/{len(checks)} checks green")
sys.exit(1 if failed else 0)
