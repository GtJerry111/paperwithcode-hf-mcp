from __future__ import annotations

from paperwithcode_mcp.parser import PaperPageData
from paperwithcode_mcp.resolver import resolve_code_link


class FakeClient:
    """A FakeClient that supports all new methods."""

    def __init__(
        self,
        page_html: str = "",
        daily_json: str = "[]",
        markdown_text: str = "",
        raise_on_fetch: bool = False,
    ):
        self.page_html = page_html
        self.daily_json = daily_json
        self.markdown_text = markdown_text
        self.raise_on_fetch = raise_on_fetch
        self.fetch_calls: list[str] = []
        self.daily_calls: list[str] = []
        self.markdown_calls: list[str] = []

    def fetch(self, arxiv_id: str) -> str:
        self.fetch_calls.append(arxiv_id)
        if self.raise_on_fetch:
            raise RuntimeError("network")
        return self.page_html

    def fetch_daily_papers(self, date: str | None = None) -> str:
        self.daily_calls.append(date or "today")
        if self.raise_on_fetch:
            raise RuntimeError("network")
        return self.daily_json

    def fetch_markdown(self, url: str) -> str:
        self.markdown_calls.append(url)
        if self.raise_on_fetch:
            raise RuntimeError("network")
        return self.markdown_text


PAGE_HTML_WITH_ALL = """<div data-target="PaperContent" data-props="{&quot;paper&quot;:{&quot;id&quot;:&quot;2508.02739&quot;,&quot;authors&quot;:[{&quot;name&quot;:&quot;Yu Shi&quot;}],&quot;title&quot;:&quot;Kronos&quot;,&quot;summary&quot;:&quot;abs&quot;,&quot;upvotes&quot;:44,&quot;githubRepo&quot;:&quot;https://github.com/shiyu-coder/Kronos&quot;,&quot;githubStars&quot;:31189},&quot;markdownContentUrl&quot;:&quot;https://example.com/paper.md&quot;}"></div>"""


def test_resolve_code_link_returns_repo_for_arxiv_id():
    client = FakeClient(page_html=PAGE_HTML_WITH_ALL)
    result = resolve_code_link({"arxiv_id": "2508.02739"}, client=client)
    assert result is not None
    assert result["github_url"] == "https://github.com/shiyu-coder/Kronos"


def test_resolve_code_link_returns_none_for_org_homepage():
    client = FakeClient(page_html='<a href="https://github.com/huggingface">Hugging Face</a>')
    assert resolve_code_link({"arxiv_id": "2508.02739"}, client=client) is None


def test_resolve_code_link_returns_none_on_network_failure():
    client = FakeClient("", raise_on_fetch=True)
    assert resolve_code_link({"arxiv_id": "2508.02739"}, client=client) is None


def test_get_paper_details_returns_paper_data():
    client = FakeClient(page_html=PAGE_HTML_WITH_ALL)
    from paperwithcode_mcp.resolver import get_paper_details

    details = get_paper_details("2508.02739", client=client)
    assert details is not None
    assert details.title == "Kronos"
    assert details.authors == ["Yu Shi"]
    assert details.upvotes == 44
    assert details.githubStars == 31189


def test_get_paper_details_returns_none_on_error():
    from paperwithcode_mcp.resolver import get_paper_details

    client = FakeClient(raise_on_fetch=True)
    assert get_paper_details("2508.02739", client=client) is None


PAGE_HTML_WITH_MARKDOWN_URL = """<div data-target="PaperContent" data-props="{&quot;paper&quot;:{&quot;id&quot;:&quot;2508.02739&quot;,&quot;authors&quot;:[{&quot;name&quot;:&quot;A&quot;}],&quot;title&quot;:&quot;T&quot;,&quot;summary&quot;:&quot;S&quot;},&quot;markdownContentUrl&quot;:&quot;https://example.com/paper.md&quot;}"></div>"""


def test_read_paper_returns_markdown():
    from paperwithcode_mcp.resolver import read_paper

    md = "# Paper Title\n\nFull text here..."
    client = FakeClient(page_html=PAGE_HTML_WITH_MARKDOWN_URL, markdown_text=md)
    result = read_paper("2508.02739", client=client)
    assert result == "# Paper Title\n\nFull text here..."
    assert client.markdown_calls == ["https://example.com/paper.md"]


def test_read_paper_returns_none_when_no_markdown_url():
    from paperwithcode_mcp.resolver import read_paper

    no_md_html = """<div data-target="PaperContent" data-props="{&quot;paper&quot;:{&quot;id&quot;:&quot;1&quot;,&quot;authors&quot;:[],&quot;title&quot;:&quot;T&quot;,&quot;summary&quot;:&quot;S&quot;}}"></div>"""
    client = FakeClient(page_html=no_md_html)
    assert read_paper("1", client=client) is None


DAILY_JSON = """[{"paper":{"id":"2606.1234","authors":[{"name":"Alice"}],"title":"Paper A","summary":"abs"},"numComments":3},{"paper":{"id":"2606.5678","authors":[{"name":"Bob"}],"title":"Paper B","summary":"abs"},"numComments":0}]"""


def test_list_daily_papers_returns_parsed_list():
    from paperwithcode_mcp.resolver import list_daily_papers, DailyPaperItem

    client = FakeClient(daily_json=DAILY_JSON)
    result = list_daily_papers(client=client)
    assert len(result) == 2
    assert isinstance(result[0], DailyPaperItem)
    assert result[0].id == "2606.1234"
    assert result[0].title == "Paper A"
    assert result[0].authors == ["Alice"]
    assert result[0].numComments == 3


def test_list_daily_papers_with_date():
    from paperwithcode_mcp.resolver import list_daily_papers

    client = FakeClient(daily_json="[]")
    result = list_daily_papers(date="2026-06-23", client=client)
    assert result == []
    assert client.daily_calls == ["2026-06-23"]


def test_list_daily_papers_returns_empty_on_error():
    from paperwithcode_mcp.resolver import list_daily_papers

    client = FakeClient(raise_on_fetch=True)
    result = list_daily_papers(client=client)
    assert result == []
