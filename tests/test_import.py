from paperwithcode_mcp import resolve_code_link, PaperPageData, PaperPageClient


def test_package_imports():
    assert callable(resolve_code_link)
    assert PaperPageData is not None
    assert PaperPageClient is not None
