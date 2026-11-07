# Repo quick-read prototype (local only, 2026-10-29)

Built a day early for the 2026-10-30 daily earning report's single next step.
Tests: 19/19 green (`python3 test_repo_quickread.py`, synthetic input only).

What it does: given already-fetched public-repo metadata, returns a compact
payload — description, topics (capped at 10), README opening summary (capped
at 600 chars, headings/badges skipped), language counts, top directories,
5 largest files, total bytes.

What it does NOT do: no GitHub API call, no repo fetch, no deployment, no
price set, no post made, nothing spent. Private repos are refused outright.
The input contract (who fetches the metadata, and how) is still undecided —
that is George's call, along with pricing and whether this or the paid
YouTube search goes live first.
