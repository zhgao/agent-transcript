"""URL -> clean Markdown, stdlib only, local prototype (not deployed).

Scope, by design:
- Fetches one public URL, strips script/style/nav/header/footer/form/svg.
- Keeps title, headings, paragraphs, lists, links (resolved to absolute),
  inline code, pre blocks and blockquotes. No account, no key, no spend.
- No paid endpoint, no wallet, no posting, no live-site change.
Usage: python3 url_to_markdown.py <url>  -> prints markdown to stdout.
"""
import sys, re, html as htmlmod
from urllib.request import Request, build_opener, ProxyHandler
from urllib.parse import urljoin
from urllib.error import URLError, HTTPError
from html.parser import HTMLParser

DROP = {"script", "style", "nav", "header", "footer", "form", "noscript", "svg", "noscript", "iframe", "select", "button"}

class MD(HTMLParser):
    def __init__(self, base):
        super().__init__(convert_charrefs=True)
        self.base = base; self.out = []; self.drop = 0; self.pre = False
        self.link = None; self.title = ""
        self._in_title = False; self._buf = ""
    def _emit(self, s):
        if s: self.out.append(s)
    def handle_starttag(self, tag, attrs):
        if tag in DROP:
            self.drop += 1; return
        if self.drop: return
        a = dict(attrs)
        if tag == "title": self._in_title = True
        elif tag in ("h1","h2","h3","h4","h5","h6"):
            self._emit("\n" + "#" * int(tag[1]) + " ")
        elif tag == "p": self._emit("\n")
        elif tag == "br": self._emit("\n")
        elif tag == "li": self._emit("\n- ")
        elif tag == "hr": self._emit("\n---\n")
        elif tag == "blockquote": self._emit("\n> ")
        elif tag == "pre": self.pre = True; self._emit("\n```\n")
        elif tag == "code" and not self.pre: self._emit("`")
        elif tag == "a" and a.get("href"):
            self.link = urljoin(self.base, a["href"]); self._emit("[")
    def handle_endtag(self, tag):
        if tag in DROP:
            self.drop = max(0, self.drop - 1); return
        if self.drop: return
        if tag == "title": self._in_title = False
        elif tag == "pre": self.pre = False; self._emit("\n```\n")
        elif tag == "code" and not self.pre: self._emit("`")
        elif tag == "a" and self.link:
            self._emit("](" + self.link + ")"); self.link = None
        elif tag in ("p","h1","h2","h3","h4","h5","h6","li"): self._emit("\n")
    def handle_data(self, data):
        if self.drop: return
        if self._in_title:
            self.title += data.strip(); return
        if not self.pre:
            data = re.sub(r"\s+", " ", data)
        if data.strip() or self.pre:
            self._emit(data if self.pre else data)
    def text(self):
        body = "".join(self.out)
        body = re.sub(r"\n{3,}", "\n\n", body).strip()
        if self.title:
            body = "# " + self.title + "\n\n" + body
        return body

def url_to_markdown(url, timeout=30):
    opener = build_opener(ProxyHandler())
    req = Request(url, headers={"User-Agent": "agent-transcript-prototype/0.1 (local test)"})
    with opener.open(req, timeout=timeout) as r:
        raw = r.read(2_000_000).decode(r.headers.get_content_charset() or "utf-8", errors="replace")
    p = MD(url); p.feed(raw); p.close()
    return p.text()

if __name__ == "__main__":
    print(url_to_markdown(sys.argv[1]))
