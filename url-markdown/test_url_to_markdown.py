import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from url_to_markdown import url_to_markdown

CASES = [
    ("https://example.com/", ["Example Domain", "documentation examples"]),
    ("https://www.python.org/", ["Python", "https://"]),
    ("https://en.wikipedia.org/wiki/History_of_the_Internet", ["History of the Internet"]),
]
fails = 0
for url, must in CASES:
    try:
        md = url_to_markdown(url)
    except Exception as e:
        print(f"FAIL fetch {url}: {e}"); fails += 1; continue
    bad = [w for w in ("<script", "<style", "function(", "var ") if w in md[:2000].lower() and w not in md.lower().replace("javascript","")]
    ok = all(m in md for m in must)
    print(f"{url} -> {len(md)} chars, contains_expected={ok}, script_leak_check={'pass' if '<script' not in md else 'FAIL'}")
    if not ok or "<script" in md:
        fails += 1
    open(f"/tmp/md_{abs(hash(url))%9999}.md", "w").write(md)
print("ALL GREEN" if fails == 0 else f"{fails} FAILURES")
sys.exit(1 if fails else 0)
