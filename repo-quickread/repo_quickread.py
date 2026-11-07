"""GitHub public-repo quick-read prototype (local, mock input only).

An agent hands over a public repo's already-fetched metadata (description,
topics, file list, README text) and gets back a compact quick-read payload:
what the repo is, what languages dominate, the biggest files, and the
README's opening summary. It never calls the GitHub API, never fetches a
repo, and never touches the live agent-transcript service.
"""

import re

_REPO_RE = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
_EXT_LANG = {
    ".py": "Python", ".js": "JavaScript", ".ts": "TypeScript",
    ".tsx": "TypeScript", ".jsx": "JavaScript", ".go": "Go",
    ".rs": "Rust", ".java": "Java", ".md": "Markdown",
    ".json": "JSON", ".yaml": "YAML", ".yml": "YAML",
    ".html": "HTML", ".css": "CSS", ".sh": "Shell",
}


def validate_repo_id(repo_id):
    """Return (owner, repo) or raise ValueError for a malformed id."""
    if not isinstance(repo_id, str) or not _REPO_RE.match(repo_id):
        raise ValueError("repo_id must look like 'owner/repo'")
    owner, repo = repo_id.split("/")
    return owner, repo


def extract_readme_summary(readme_text, max_chars=600):
    """First non-heading, non-empty paragraph of the README, capped."""
    if not readme_text:
        return ""
    lines = []
    for raw in readme_text.splitlines():
        line = raw.strip()
        if not line:
            if lines:
                break
            continue
        if line.startswith("#"):
            continue
        if line.startswith("![") or line.startswith("[!["):
            continue
        lines.append(line)
    summary = " ".join(lines)
    return summary[:max_chars]


def summarize_files(files, max_files=50):
    """Summarize a file list: [{path, size_bytes}]. Capped, sorted output."""
    files = list(files or [])[:max_files]
    languages = {}
    top_dirs = {}
    largest = sorted(files, key=lambda f: f.get("size_bytes", 0), reverse=True)[:5]
    for f in files:
        path = f.get("path", "")
        ext = "." + path.rsplit(".", 1)[-1].lower() if "." in path.rsplit("/", 1)[-1] else ""
        lang = _EXT_LANG.get(ext, ext[1:].upper() if ext else "other")
        languages[lang] = languages.get(lang, 0) + 1
        top = path.split("/")[0] if "/" in path else "(root)"
        top_dirs[top] = top_dirs.get(top, 0) + 1
    return {
        "file_count": len(files),
        "total_bytes": sum(f.get("size_bytes", 0) for f in files),
        "languages": dict(sorted(languages.items(), key=lambda kv: -kv[1])),
        "top_dirs": dict(sorted(top_dirs.items(), key=lambda kv: -kv[1])),
        "largest_files": [
            {"path": f.get("path", ""), "size_bytes": f.get("size_bytes", 0)}
            for f in largest
        ],
    }


def quickread(repo_id, description="", topics=None, files=None,
              readme_text="", is_public=True):
    """Build the quick-read payload. Private repos are refused, not summarized."""
    if not is_public:
        raise ValueError("only public repos are supported")
    owner, repo = validate_repo_id(repo_id)
    payload = {
        "repo": repo_id,
        "owner": owner,
        "name": repo,
        "description": (description or "")[:200],
        "topics": list(topics or [])[:10],
        "readme_summary": extract_readme_summary(readme_text),
        "source": "mock input only — no GitHub API call was made",
    }
    payload.update(summarize_files(files))
    return payload
