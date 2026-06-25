# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

- Install project: `pip install -e ".[dev]"`
- Run server (stdio): `paperwithcode-mcp`
- Run server (SSE): `paperwithcode-mcp --transport sse --host 127.0.0.1 --port 8787`
- Run server from source (no install): `PYTHONPATH=src python3 -m paperwithcode_mcp`
- Run tests: `python3 -m pytest tests/ -v`
- Run a single test: `python3 -m pytest tests/test_parser.py::test_extract_paper_page_data_returns_all_fields -v`
- Build Docker: `docker build -t paperwithcode-mcp .`

## Architecture

MCP server that resolves `arxiv_id -> github_url` and provides paper reading capabilities from Hugging Face Papers. Built with FastMCP SDK, supports stdio (Claude Desktop) and SSE (remote) transports.

### Flow

`MCP tool call` → `mcp_server.py` (FastMCP) → `resolver.py` (business logic) → `client.py` (curl) + `parser.py` (HTML data extraction)

### Key modules

- **`mcp_server.py`** — FastMCP server, defines 4 tools and `cli()` console entry point
- **`client.py`** — `PaperPageClient`, network layer via curl subprocess
- **`parser.py`** — HTML parsing. `extract_paper_page_data()` → `PaperPageData` dataclass
- **`resolver.py`** — Business logic: 4 resolver functions

### Data sources

- `https://huggingface.co/papers/{arxiv_id}` — single paper page (scraped for data-props JSON)
- `https://huggingface.co/api/daily_papers?date=YYYY-MM-DD` — daily listings API (no auth required)
- `markdownContentUrl` — full paper text as markdown from arXiv HTML

### Project boundaries

This project uses Hugging Face Papers, NOT the paperswithcode.com API (deprecated).
- ✅ arxiv_id → metadata / GitHub URL / full text / daily listings
- ❌ No paper search, no author/conference browsing, no benchmarks/datasets

### Testing patterns

Tests use dependency injection: custom `FakeClient` objects replace `PaperPageClient` to avoid real HTTP calls.

### Configuration (env vars)

- `HTTPS_PROXY` / `HTTP_PROXY` / `ALL_PROXY` — proxy for curl
- `PWC_TIMEOUT` — curl timeout in seconds (default: 15.0)
