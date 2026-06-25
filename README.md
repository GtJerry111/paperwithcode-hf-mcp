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

### `resolve_code_link`

Resolve an arXiv ID to its GitHub repository URL.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `arxiv_id` | `string` | Yes | The arXiv paper ID (e.g. `2508.02739`) |

**Returns:** `{ "github_url": "https://github.com/shiyu-coder/Kronos" }`

Returns `null` if no GitHub repository is found for the given paper.

### `get_paper_details`

Get detailed paper metadata from Hugging Face Papers.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `arxiv_id` | `string` | Yes | The arXiv paper ID (e.g. `2508.02739`) |

**Returns:** JSON object with:
- `id` — arXiv ID
- `title` — paper title
- `authors` — list of author names
- `publishedAt` — publication date
- `summary` — abstract text
- `upvotes` — upvote count on Hugging Face
- `githubRepo` — linked GitHub repository URL (if any)
- `githubStars` — GitHub star count (if repo exists)
- `ai_summary` — AI-generated summary
- `ai_keywords` — list of AI-extracted keywords
- `discussionId` — Hugging Face discussion thread ID
- `markdownContentUrl` — URL to the full paper markdown

Returns `null` if the paper is not found.

### `read_paper`

Fetch the full text of a paper as markdown.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `arxiv_id` | `string` | Yes | The arXiv paper ID (e.g. `2508.02739`) |

**Returns:** A markdown string containing the complete paper text (abstract, introduction, method, results, etc.). Returns `null` if the paper cannot be found or has no markdown source.

### `list_daily_papers`

List papers featured on Hugging Face Papers for a given date.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `date` | `string` | No | Date in `YYYY-MM-DD` format. Defaults to today if omitted. |

**Returns:** A list of papers, each containing:
- `id` — arXiv ID
- `title` — paper title
- `authors` — list of author names
- `publishedAt` — publication date
- `summary` — abstract
- `upvotes` — upvote count
- `numComments` — number of comments on Hugging Face

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
