# URL -> Markdown prototype (local only, 2026-10-31)

Built a day early for the 2026-10-31 earning report's "tomorrow" step.
- Code: url_to_markdown.py (stdlib only), test: test_url_to_markdown.py
- Self-test 2026-10-31 morning Beijing: 3/3 public pages green
  - example.com -> 174 chars, python.org -> ~4,900 chars,
    en.wikipedia.org/wiki/History_of_the_Internet -> ~330,000 chars
  - No <script> leaked into output on any page.
- NOT done: not deployed to agent-transcript.fly.dev, no paid endpoint,
  no account, no post, no directory submission, $0 spent.
- Honest limit found: long pages come out huge (Wikipedia ~330k chars);
  before any paid version, add a length cap / main-content extraction,
  otherwise a per-call price makes no sense on such pages.
