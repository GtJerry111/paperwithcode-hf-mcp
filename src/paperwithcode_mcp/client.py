from __future__ import annotations

import subprocess
import time
from dataclasses import dataclass
from os import getenv
from urllib.parse import urljoin


@dataclass
class PaperPageClient:
    base_url: str | None = None
    timeout: float | None = None
    proxy_url: str | None = None
    auto_proxy: bool = True

    def __post_init__(self) -> None:
        if self.base_url is None:
            self.base_url = getenv("PWC_BASE_URL", "https://huggingface.co/papers")
        if self.timeout is None:
            self.timeout = float(getenv("PWC_TIMEOUT", "15.0"))
        if self.proxy_url is None and getenv("PWC_PROXY_URL"):
            self.proxy_url = getenv("PWC_PROXY_URL")

    def _effective_proxy_url(self) -> str | None:
        if self.proxy_url is not None:
            return self.proxy_url
        if not self.auto_proxy:
            return None
        return (
            getenv("HTTPS_PROXY")
            or getenv("https_proxy")
            or getenv("HTTP_PROXY")
            or getenv("http_proxy")
            or getenv("ALL_PROXY")
            or getenv("all_proxy")
        )

    def _curl(self, url: str) -> str:
        command = [
            "curl",
            "-L",
            "--http1.1",
            "--retry", "2",
            "--retry-all-errors",
            "--retry-delay", "1",
            "--connect-timeout", "10",
            "--silent",
            "--show-error",
            "--max-time", str(int(self.timeout)),
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

    def fetch(self, arxiv_id: str) -> str:
        """Fetch the HTML of a single paper page from HF Papers."""
        url = urljoin(self.base_url.rstrip("/") + "/", arxiv_id)
        return self._curl(url)

    def fetch_daily_papers(self, date: str | None = None) -> str:
        """Fetch the daily papers listing JSON from the HF API."""
        url = "https://huggingface.co/api/daily_papers"
        if date:
            url = f"{url}?date={date}"
        return self._curl(url)

    def fetch_markdown(self, url: str) -> str:
        """Fetch content from a URL (typically the paper markdown content URL)."""
        return self._curl(url)
