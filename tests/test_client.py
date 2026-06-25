from paperwithcode_mcp.client import extract_repo_url


def test_extract_repo_url_prefers_github_repo_field():
    html = '<script>{"githubRepo":"https://github.com/shiyu-coder/Kronos"}</script>'
    assert extract_repo_url(html) == "https://github.com/shiyu-coder/Kronos"


def test_extract_repo_url_accepts_explicit_repo_link():
    html = '<a href="https://github.com/org/repo">Repo</a>'
    assert extract_repo_url(html) == "https://github.com/org/repo"


def test_extract_repo_url_rejects_org_homepage():
    html = '<a href="https://github.com/huggingface">Hugging Face</a>'
    assert extract_repo_url(html) is None

