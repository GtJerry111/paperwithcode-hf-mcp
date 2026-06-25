from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any

from .client import PaperPageClient
from .parser import PaperPageData, extract_paper_page_data, extract_repo_url


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


@dataclass
class DailyPaperItem:
    id: str
    title: str
    authors: list[str] = field(default_factory=list)
    summary: str | None = None
    publishedAt: str | None = None
    upvotes: int = 0
    numComments: int = 0


def get_paper_details(arxiv_id: str, client: PaperPageClient | None = None) -> PaperPageData | None:
    """Fetch and parse full paper metadata for a given arXiv ID."""
    client = client or PaperPageClient()
    try:
        html = client.fetch(arxiv_id)
    except Exception:
        return None
    return extract_paper_page_data(html)


def read_paper(arxiv_id: str, client: PaperPageClient | None = None) -> str | None:
    """Fetch the full paper text as markdown for a given arXiv ID."""
    client = client or PaperPageClient()
    try:
        html = client.fetch(arxiv_id)
    except Exception:
        return None
    data = extract_paper_page_data(html)
    if not data or not data.markdownContentUrl:
        return None
    try:
        return client.fetch_markdown(data.markdownContentUrl)
    except Exception:
        return None


def list_daily_papers(date: str | None = None, client: PaperPageClient | None = None) -> list[DailyPaperItem]:
    """Fetch and parse the daily papers listing from HF Papers."""
    client = client or PaperPageClient()
    try:
        raw = client.fetch_daily_papers(date)
    except Exception:
        return []
    try:
        entries = json.loads(raw)
    except (json.JSONDecodeError, ValueError):
        return []
    results: list[DailyPaperItem] = []
    for entry in entries:
        paper = entry.get("paper", {})
        if not paper.get("id"):
            continue
        authors = []
        for a in paper.get("authors", []):
            if isinstance(a, dict) and a.get("name"):
                authors.append(a["name"])
        results.append(
            DailyPaperItem(
                id=paper["id"],
                title=paper.get("title", ""),
                authors=authors,
                summary=paper.get("summary"),
                publishedAt=paper.get("publishedAt"),
                upvotes=paper.get("upvotes", 0),
                numComments=entry.get("numComments", 0),
            )
        )
    return results

