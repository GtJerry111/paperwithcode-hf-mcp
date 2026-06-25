from __future__ import annotations

from paperwithcode_mcp.mcp_server import create_server, main


def test_create_server_returns_fastmcp_instance():
    server = create_server()
    assert server is not None
    assert server.name == "paperwithcode-mcp"


def test_main_parses_help():
    try:
        main(["--help"])
    except SystemExit as e:
        assert e.code == 0


def test_main_sse_transport():
    """main() with --transport sse should parse correctly.
    We mock mcp.run to prevent server start."""
    from paperwithcode_mcp import mcp_server
    original_run = mcp_server.mcp.run
    try:
        calls = []
        def fake_run(**kwargs):
            calls.append(kwargs)
        mcp_server.mcp.run = fake_run
        mcp_server.main(["--transport", "sse", "--host", "0.0.0.0", "--port", "9999"])
        assert calls == [{"transport": "sse", "host": "0.0.0.0", "port": 9999}]
    finally:
        mcp_server.mcp.run = original_run


SAMPLE_PAGE_HTML = """<div data-target="PaperContent" data-props="{&quot;paper&quot;:{&quot;id&quot;:&quot;2508.02739&quot;,&quot;authors&quot;:[{&quot;name&quot;:&quot;Yu Shi&quot;}],&quot;title&quot;:&quot;Kronos&quot;,&quot;summary&quot;:&quot;Abstract text&quot;,&quot;upvotes&quot;:44,&quot;githubRepo&quot;:&quot;https://github.com/shiyu-coder/Kronos&quot;,&quot;githubStars&quot;:31189},&quot;markdownContentUrl&quot;:&quot;https://example.com/md&quot;}"></div>"""


def test_tools_are_callable_via_resolver():
    from paperwithcode_mcp.resolver import get_paper_details, list_daily_papers, read_paper, resolve_code_link

    class MockClient:
        def fetch(self, arxiv_id):
            return SAMPLE_PAGE_HTML
        def fetch_daily_papers(self, date=None):
            return """[{"paper":{"id":"2606.1234","authors":[{"name":"Alice"}],"title":"Paper A","summary":"abs"},"numComments":3}]"""
        def fetch_markdown(self, url):
            return "# Markdown Content"

    client = MockClient()

    # resolve_code_link
    result = resolve_code_link({"arxiv_id": "2508.02739"}, client=client)
    assert result is not None
    assert result["github_url"] == "https://github.com/shiyu-coder/Kronos"

    # get_paper_details
    data = get_paper_details("2508.02739", client=client)
    assert data is not None
    assert data.title == "Kronos"
    assert data.upvotes == 44

    # read_paper
    md = read_paper("2508.02739", client=client)
    assert md == "# Markdown Content"

    # list_daily_papers
    papers = list_daily_papers(client=client)
    assert len(papers) == 1
    assert papers[0].title == "Paper A"
