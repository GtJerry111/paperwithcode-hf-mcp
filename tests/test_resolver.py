from paperwithcode_mcp.resolver import resolve_code_link


class FakeClient:
    def __init__(self, html: str, raise_on_fetch: bool = False):
        self.html = html
        self.raise_on_fetch = raise_on_fetch
        self.calls = []

    def fetch(self, arxiv_id: str) -> str:
        self.calls.append(arxiv_id)
        if self.raise_on_fetch:
            raise RuntimeError("network")
        return self.html


def test_resolve_code_link_returns_repo_for_arxiv_id():
    client = FakeClient('<script>{"githubRepo":"https://github.com/shiyu-coder/Kronos"}</script>')
    result = resolve_code_link({"arxiv_id": "2508.02739"}, client=client)
    assert result == {
        "github_url": "https://github.com/shiyu-coder/Kronos",
        "paper_url": "https://huggingface.co/papers/2508.02739",
        "matched_by": "arxiv_id",
        "confidence": "high",
    }


def test_resolve_code_link_returns_none_for_org_homepage():
    client = FakeClient('<a href="https://github.com/huggingface">Hugging Face</a>')
    assert resolve_code_link({"arxiv_id": "2508.02739"}, client=client) is None


def test_resolve_code_link_returns_none_on_network_failure():
    client = FakeClient("", raise_on_fetch=True)
    assert resolve_code_link({"arxiv_id": "2508.02739"}, client=client) is None

