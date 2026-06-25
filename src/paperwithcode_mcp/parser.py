from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from html.parser import HTMLParser
from typing import Any

GITHUB_REPO_RE = re.compile(r"https://github\.com/[^\"'\s<>/]+/[^\"'\s<>/]+(?:/[^\"'\s<>/]*)?")
GITHUB_REPO_FIELD_RE = re.compile(r'"githubRepo"\s*:\s*"([^"]+)"')

# Regex to extract the JSON blob from data-target="PaperContent" data-props="..."
PAPER_CONTENT_PROPS_RE = re.compile(
    r'data-target="PaperContent"\s*data-props="([^"]+)"'
)


@dataclass
class PaperPageData:
    id: str
    title: str
    authors: list[str] = field(default_factory=list)
    publishedAt: str | None = None
    summary: str | None = None
    upvotes: int = 0
    githubRepo: str | None = None
    githubStars: int | None = None
    ai_summary: str | None = None
    ai_keywords: list[str] | None = None
    discussionId: str | None = None
    markdownContentUrl: str | None = None


class _GithubLinkCollector(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.repo_urls: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag != "a":
            return
        attrs_dict = dict(attrs)
        href = attrs_dict.get("href") or ""
        if GITHUB_REPO_RE.fullmatch(href):
            self.repo_urls.append(href)


def _clean_repo_url(url: str) -> str | None:
    cleaned = url.replace("&quot;", '"').strip().rstrip('".,;)]}>')
    if GITHUB_REPO_RE.fullmatch(cleaned):
        return cleaned
    return None


def extract_repo_url(html: str) -> str | None:
    """Extract the first GitHub repository URL from a HF Papers page HTML."""
    match = GITHUB_REPO_FIELD_RE.search(html)
    if match:
        cleaned = _clean_repo_url(match.group(1))
        if cleaned:
            return cleaned

    parser = _GithubLinkCollector()
    parser.feed(html)
    for repo_url in parser.repo_urls:
        cleaned = _clean_repo_url(repo_url)
        if cleaned:
            return cleaned
    return None


def _extract_json_props(html: str) -> dict[str, Any] | None:
    """Extract and parse the JSON from PaperContent data-props."""
    import html as html_mod

    match = PAPER_CONTENT_PROPS_RE.search(html)
    if not match:
        return None
    try:
        raw = html_mod.unescape(match.group(1))
        return json.loads(raw)
    except (json.JSONDecodeError, ValueError):
        return None


def extract_paper_page_data(html: str) -> PaperPageData | None:
    """Extract structured paper metadata from a HF Papers page HTML."""
    props = _extract_json_props(html)
    if props is None:
        return None

    paper = props.get("paper")
    if not paper or not isinstance(paper, dict):
        return None

    paper_id = paper.get("id", "")
    if not paper_id:
        return None

    authors = []
    for a in paper.get("authors", []):
        if isinstance(a, dict) and a.get("name"):
            authors.append(a["name"])

    return PaperPageData(
        id=paper_id,
        title=paper.get("title", ""),
        authors=authors,
        publishedAt=paper.get("publishedAt"),
        summary=paper.get("summary"),
        upvotes=paper.get("upvotes", 0),
        githubRepo=paper.get("githubRepo"),
        githubStars=paper.get("githubStars"),
        ai_summary=paper.get("ai_summary"),
        ai_keywords=paper.get("ai_keywords"),
        discussionId=paper.get("discussionId"),
        markdownContentUrl=props.get("markdownContentUrl"),
    )
