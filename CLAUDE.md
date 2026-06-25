# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### pip
- Install: `pip install -e ".[dev]"`
- Run tests: `python3 -m pytest tests/ -v`
- Run single test: `python3 -m pytest tests/test_parser.py::test_extract_paper_page_data_returns_all_fields -v`
- Run server: `paperwithcode-mcp`

### uv
- Sync: `uv sync --group dev`
- Run tests: `uv run pytest tests/ -v`
- Install as tool: `uv tool install .`
- Run server (from source): `uv run python -m paperwithcode_mcp`

### Docker
- Build: `docker build -t paperwithcode-mcp .`
- Run (stdio): `docker run -i --rm paperwithcode-mcp`
- Run (SSE): `docker run -i --rm -p 8787:8787 paperwithcode-mcp --transport sse --host 0.0.0.0 --port 8787`

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
