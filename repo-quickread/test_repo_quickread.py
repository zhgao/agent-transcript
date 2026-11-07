import sys
sys.path.insert(0, ".")
from repo_quickread import validate_repo_id, extract_readme_summary, summarize_files, quickread

passed = failed = 0
def check(name, cond):
    global passed, failed
    if cond:
        passed += 1
    else:
        failed += 1
        print("FAIL:", name)

check("valid id splits", validate_repo_id("zhgao/nightshift-free") == ("zhgao", "nightshift-free"))
for bad in ["", "noslash", "a/b/c", "owner /repo", "owner/"]:
    try:
        validate_repo_id(bad); check("reject %r" % bad, False)
    except ValueError:
        check("reject %r" % bad, True)
def _private():
    try:
        quickread("a/b", is_public=False); return False
    except ValueError:
        return True
check("private refused", _private())

check("readme skips heading/badge", extract_readme_summary("# Title\n\n![x](y)\n\nReal summary here.\n\nMore.") == "Real summary here.")
check("readme empty", extract_readme_summary("") == "")
check("readme capped", len(extract_readme_summary("word " * 200)) == 600)

files = [
    {"path": "src/main.py", "size_bytes": 9000},
    {"path": "src/util.py", "size_bytes": 3000},
    {"path": "README.md", "size_bytes": 500},
    {"path": "web/app.ts", "size_bytes": 12000},
]
s = summarize_files(files)
check("file count", s["file_count"] == 4)
check("languages", s["languages"] == {"Python": 2, "Markdown": 1, "TypeScript": 1})
check("largest first", s["largest_files"][0]["path"] == "web/app.ts")
check("total bytes", s["total_bytes"] == 24500)
check("top dirs", s["top_dirs"]["src"] == 2)

q = quickread("zhgao/nightshift-free", description="6-tool overnight pipeline",
              topics=["ai", "automation"], files=files,
              readme_text="# NightShift\n\nShips a landing page overnight.")
check("payload repo", q["repo"] == "zhgao/nightshift-free")
check("payload summary", q["readme_summary"] == "Ships a landing page overnight.")
check("empty repo ok", quickread("a/b")["file_count"] == 0)
check("topics capped", len(quickread("a/b", topics=["t"] * 15)["topics"]) == 10)

print(f"{passed} passed, {failed} failed")
raise SystemExit(1 if failed else 0)
