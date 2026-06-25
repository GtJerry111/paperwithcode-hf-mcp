from paperwithcode_mcp.client import PaperPageClient

import json
import pytest


def test_fetch_daily_papers_returns_list():
    """Integration test: depends on network. Skipped unless INTEGRATION_TEST=1."""
    import os
    if not os.environ.get("INTEGRATION_TEST"):
        pytest.skip("set INTEGRATION_TEST=1 to run")

    client = PaperPageClient()
    data = client.fetch_daily_papers()
    assert isinstance(data, str)
    parsed = json.loads(data)
    assert isinstance(parsed, list)
    assert len(parsed) > 0
    assert "paper" in parsed[0]


def test_fetch_daily_papers_with_date():
    client = PaperPageClient()
    data = client.fetch_daily_papers("2026-06-23")
    assert isinstance(data, str)
    parsed = json.loads(data)
    assert isinstance(parsed, list)
