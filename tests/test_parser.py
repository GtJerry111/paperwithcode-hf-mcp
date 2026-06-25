from __future__ import annotations

from paperwithcode_mcp.parser import extract_paper_page_data, extract_repo_url


# --- extract_repo_url ---

SAMPLE_HTML_WITH_REPO = """<div>Some content</div>
<script>{"githubRepo":"https://github.com/shiyu-coder/Kronos"}</script>"""


def test_extract_repo_url_prefers_github_repo_field():
    assert extract_repo_url(SAMPLE_HTML_WITH_REPO) == "https://github.com/shiyu-coder/Kronos"


SAMPLE_HTML_WITH_A_TAG = '<a href="https://github.com/org/repo">Repo</a>'


def test_extract_repo_url_accepts_explicit_repo_link():
    assert extract_repo_url(SAMPLE_HTML_WITH_A_TAG) == "https://github.com/org/repo"


SAMPLE_HTML_ORG_ONLY = '<a href="https://github.com/huggingface">Hugging Face</a>'


def test_extract_repo_url_rejects_org_homepage():
    assert extract_repo_url(SAMPLE_HTML_ORG_ONLY) is None


# --- extract_paper_page_data ---

SAMPLE_PAGE_HTML = """<div data-target="PaperContent" data-props="{&quot;paper&quot;:{&quot;id&quot;:&quot;2508.02739&quot;,&quot;authors&quot;:[{&quot;name&quot;:&quot;Yu Shi&quot;}],&quot;publishedAt&quot;:&quot;2025-08-02T13:15:59.000Z&quot;,&quot;title&quot;:&quot;Kronos: A Foundation Model&quot;,&quot;summary&quot;:&quot;The success of large-scale pre-training...&quot;,&quot;upvotes&quot;:44,&quot;githubRepo&quot;:&quot;https://github.com/shiyu-coder/Kronos&quot;,&quot;githubStars&quot;:31189,&quot;ai_summary&quot;:&quot;Kronos, a specialized...&quot;,&quot;ai_keywords&quot;:[&quot;LLM&quot;,&quot;Finance&quot;],&quot;discussionId&quot;:&quot;abc123&quot;},&quot;markdownContentUrl&quot;:&quot;https://hf.co/buckets/...md&quot;}"></div>"""


def test_extract_paper_page_data_returns_all_fields():
    data = extract_paper_page_data(SAMPLE_PAGE_HTML)
    assert data.id == "2508.02739"
    assert data.title == "Kronos: A Foundation Model"
    assert data.authors == ["Yu Shi"]
    assert data.publishedAt == "2025-08-02T13:15:59.000Z"
    assert data.summary == "The success of large-scale pre-training..."
    assert data.upvotes == 44
    assert data.githubRepo == "https://github.com/shiyu-coder/Kronos"
    assert data.githubStars == 31189
    assert data.ai_summary == "Kronos, a specialized..."
    assert data.ai_keywords == ["LLM", "Finance"]
    assert data.discussionId == "abc123"
    assert data.markdownContentUrl == "https://hf.co/buckets/...md"


SAMPLE_HTML_NO_PAPER = "<html><body>No paper here</body></html>"


def test_extract_paper_page_data_returns_none_when_missing():
    assert extract_paper_page_data(SAMPLE_HTML_NO_PAPER) is None


SAMPLE_HTML_NO_REPO = """<div data-target="PaperContent" data-props="{&quot;paper&quot;:{&quot;id&quot;:&quot;2508.02739&quot;,&quot;authors&quot;:[],&quot;title&quot;:&quot;Test&quot;,&quot;summary&quot;:&quot;abs&quot;,&quot;upvotes&quot;:0}}"></div>"""


def test_extract_paper_page_data_handles_missing_optional_fields():
    data = extract_paper_page_data(SAMPLE_HTML_NO_REPO)
    assert data is not None
    assert data.githubRepo is None
    assert data.githubStars is None
    assert data.ai_summary is None
    assert data.ai_keywords is None
    assert data.markdownContentUrl is None
    assert data.publishedAt is None
    assert data.discussionId is None


SAMPLE_EMPTY = ""


def test_extract_repo_url_returns_none_on_empty():
    assert extract_repo_url(SAMPLE_EMPTY) is None
