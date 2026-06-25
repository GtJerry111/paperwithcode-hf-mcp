# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

- Run server (stdio): `PYTHONPATH=src python3 -m paperwithcode_mcp`
- Run server (SSE): `PYTHONPATH=src python3 -m paperwithcode_mcp --transport sse --host 127.0.0.1 --port 8787`
- Run tests: `python3 -m pytest tests/ -v`
- Run a single test: `python3 -m pytest tests/test_parser.py::test_extract_paper_page_data_returns_all_fields -v`
- Install dev deps: `pip install -e ".[dev]"`

## Architecture

MCP server that resolves `arxiv_id -> github_url` and provides paper reading capabilities from Hugging Face Papers. Built with FastMCP SDK, supports stdio (Claude Desktop) and SSE (remote) transports.

### Flow

`MCP tool call` → `mcp_server.py` (FastMCP) → `resolver.py` (business logic) → `client.py` (curl) + `parser.py` (HTML data extraction)

### Key modules

- **`mcp_server.py`** — FastMCP server, defines tools: `resolve_code_link`, `get_paper_details`, `read_paper`, `list_daily_papers`
- **`client.py`** — `PaperPageClient`, network layer via curl subprocess. Methods: `fetch(arxiv_id)`, `fetch_daily_papers(date)`, `fetch_markdown(url)`
- **`parser.py`** — HTML parsing. `extract_paper_page_data(html)` → `PaperPageData` dataclass with title/authors/summary/githubRepo/githubStars/ai_summary/ai_keywords/upvotes. `extract_repo_url(html)` → GitHub URL.
- **`resolver.py`** — Business logic: `resolve_code_link`, `get_paper_details`, `read_paper`, `list_daily_papers`

### Data sources

- `https://huggingface.co/papers/{arxiv_id}` — single paper page (scraped for data-props JSON)
- `https://huggingface.co/api/daily_papers?date=YYYY-MM-DD` — daily listings API (no auth required)
- `markdownContentUrl` — full paper text as markdown from arXiv HTML

### Testing patterns

Tests use dependency injection: custom `FakeClient` objects replace `PaperPageClient` to avoid real HTTP calls. Each test file tests one module.

### Configuration (env vars)

- `HTTPS_PROXY` / `HTTP_PROXY` / `ALL_PROXY` — proxy for curl
- `PWC_TIMEOUT` — curl timeout in seconds (default: 15.0)
