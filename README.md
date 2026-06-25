# paperwithcode-mcp

MCP server that brings AI paper reading and code repository discovery from [Hugging Face Papers](https://huggingface.co/papers) into any MCP-compatible client (Claude Desktop, IDE plugins, etc.). Supports both stdio and SSE transports.

## Overview

Keeping up with AI research means reading papers, finding code implementations, and tracking daily new releases. This server bridges Hugging Face Papers' rich metadata — AI summaries, GitHub star counts, full paper markdown, and daily trending lists — directly into your AI assistant's toolset. Instead of switching between browser tabs, you query papers conversationally.

**What you can do:**

- Paste an arXiv ID and get the corresponding GitHub repo (with star count)
- Ask for a paper's details: title, authors, abstract, AI summary, keywords
- Read a paper's full text as markdown in your conversation
- List today's trending papers on Hugging Face Papers

## Quick Start

```bash
pip install git+https://github.com/GtJerry111/paperwithcode-hf-mcp.git
paperwithcode-mcp
```

The server starts in stdio mode, ready to connect to Claude Desktop or any MCP host. Add it to your `claude_desktop_config.json` (see [Claude Desktop Integration](#claude-desktop-integration)) and you're done.

## Tools

| Tool | Description |
|------|-------------|
| `resolve_code_link` | Given an arXiv ID, return its GitHub repository URL |
| `get_paper_details` | Return full metadata: title, authors, abstract, GitHub stars, AI summary, keywords, upvotes |
| `read_paper` | Fetch the complete paper text as markdown (converted from arXiv HTML) |
| `list_daily_papers` | Return the papers featured on Hugging Face Papers for a given date |

### Usage Examples

Each tool accepts simple string arguments and returns JSON. Here is what you can expect from each:

**resolve_code_link** — `"2508.02739"` returns `{"github_url": "https://github.com/shiyu-coder/Kronos"}`

**get_paper_details** — `"2508.02739"` returns a rich object with title, authors (list), summary, upvotes (integer), githubStars (integer), ai_summary (string), ai_keywords (list), and more.

**read_paper** — `"2508.02739"` returns the full paper as a markdown string (all sections: abstract, introduction, method, results, etc.).

**list_daily_papers** — `"2026-06-23"` returns up to 50 papers with id, title, authors, summary, upvotes, and comment count. Omit the date to get today's papers.

## Deployment

### pip

```bash
pip install git+https://github.com/GtJerry111/paperwithcode-hf-mcp.git

paperwithcode-mcp                                        # stdio (default)
paperwithcode-mcp --transport sse --host 0.0.0.0 --port 8787  # SSE
```

### uv

```bash
uv tool install git+https://github.com/GtJerry111/paperwithcode-hf-mcp.git

paperwithcode-mcp                                        # stdio

# Update later
uv tool upgrade paperwithcode-mcp
```

### Docker

```bash
docker build -t paperwithcode-mcp .
docker run -i --rm paperwithcode-mcp                     # stdio
docker run -i --rm -p 8787:8787 paperwithcode-mcp \
  --transport sse --host 0.0.0.0 --port 8787              # SSE
```

## Claude Desktop Integration

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "paperwithcode": {
      "command": "paperwithcode-mcp",
      "args": []
    }
  }
}
```

If `paperwithcode-mcp` is not in your PATH after pip install, use the full Python module path or the uvx launcher:

```json
{
  "mcpServers": {
    "paperwithcode": {
      "command": "uvx",
      "args": ["paperwithcode-mcp"]
    }
  }
}
```

## Development

```bash
git clone https://github.com/GtJerry111/paperwithcode-hf-mcp.git
cd paperwithcode-hf-mcp

# pip
pip install -e ".[dev]"

# uv
uv sync --group dev
```

### Architecture

The server has a simple data flow:

```
MCP tool call -> mcp_server.py (FastMCP) -> resolver.py (business logic)
    -> client.py (curl/network) + parser.py (HTML extraction)
```

- **mcp_server.py** — FastMCP instance with 4 tool definitions and the CLI entry point
- **resolver.py** — orchestrates calls between client and parser, returns typed results
- **client.py** — `PaperPageClient` wraps curl subprocess, handles proxy and retries
- **parser.py** — extracts structured data from Hugging Face paper pages

### Data Sources

- `https://huggingface.co/papers/{arxiv_id}` — individual paper page (embedded JSON in `data-props`)
- `https://huggingface.co/api/daily_papers?date=YYYY-MM-DD` — daily papers API (no auth)
- `markdownContentUrl` — full paper text as markdown from the arXiv HTML conversion

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HTTPS_PROXY` / `HTTP_PROXY` / `ALL_PROXY` | — | Proxy for outgoing HTTP requests |
| `PWC_TIMEOUT` | `15.0` | Request timeout in seconds |

## Limitations

This project uses **Hugging Face Papers** as its data source, NOT the paperswithcode.com API (which is no longer available). As a result:

- No paper search by keyword or title
- No conference, proceedings, or author browsing
- No benchmark results or dataset listings

## License

MIT
