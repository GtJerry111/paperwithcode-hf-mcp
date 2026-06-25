from __future__ import annotations

import re
import subprocess
import time
from dataclasses import dataclass
from html.parser import HTMLParser
from os import getenv
from urllib.parse import urljoin

GITHUB_REPO_RE = re.compile(r"https://github\.com/[^\"'\s<>/]+/[^\"'\s<>/]+(?:/[^\"'\s<>/]*)?")
GITHUB_REPO_FIELD_RE = re.compile(r'"githubRepo"\s*:\s*"([^"]+)"')


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


@dataclass
class PaperPageClient:
    base_url: str = "https://huggingface.co/papers"
    timeout: float = 15.0
    proxy_url: str | None = None
    auto_proxy: bool = True

    def _effective_proxy_url(self) -> str | None:
        if self.proxy_url is not None:
            return self.proxy_url
        if not self.auto_proxy:
            return None
        return (
            getenv("PWC_PROXY_URL")
            or getenv("HTTPS_PROXY")
            or getenv("https_proxy")
            or getenv("HTTP_PROXY")
            or getenv("http_proxy")
            or getenv("ALL_PROXY")
            or getenv("all_proxy")
        )

    def fetch(self, arxiv_id: str) -> str:
        url = urljoin(self.base_url.rstrip("/") + "/", arxiv_id)
        command = [
            "curl",
            "-L",
            "--http1.1",
            "--retry",
            "2",
            "--retry-all-errors",
            "--retry-delay",
            "1",
            "--connect-timeout",
            "10",
            "--silent",
            "--show-error",
            "--max-time",
            str(int(self.timeout)),
            url,
        ]
        proxy_url = self._effective_proxy_url()
        if proxy_url:
            command[1:1] = ["--proxy", proxy_url]
        last_error: subprocess.CalledProcessError | None = None
        for attempt in range(2):
            try:
                completed = subprocess.run(command, check=True, capture_output=True, text=True)
                return completed.stdout
            except subprocess.CalledProcessError as exc:
                last_error = exc
                if attempt == 0:
                    time.sleep(1)
        raise last_error  # type: ignore[misc]
