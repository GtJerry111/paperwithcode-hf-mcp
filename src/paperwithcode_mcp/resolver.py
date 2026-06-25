from __future__ import annotations

from typing import Any

from .client import PaperPageClient, extract_repo_url


def _is_repo_url(url: str | None) -> bool:
    return bool(url and url.startswith("https://github.com/") and url.count("/") >= 4)


def resolve_code_link(query: dict[str, Any], client: PaperPageClient | None = None) -> dict[str, Any] | None:
    arxiv_id = query.get("arxiv_id")
    if not arxiv_id:
        return None

    client = client or PaperPageClient()
    try:
        html = client.fetch(arxiv_id)
    except Exception:
        return None

    repo_url = extract_repo_url(html)
    if not _is_repo_url(repo_url):
        return None

    return {
        "github_url": repo_url,
        "paper_url": f"https://huggingface.co/papers/{arxiv_id}",
        "matched_by": "arxiv_id",
        "confidence": "high",
    }

