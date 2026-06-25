# paperwithcode_mcp

MCP server that provides paper reading and code repository discovery from Hugging Face Papers. Supports both stdio (Claude Desktop) and SSE (remote) transports.

## Features

- **resolve_code_link** — Resolve an arXiv ID to its GitHub repository URL
- **get_paper_details** — Get paper metadata: title, authors, abstract, GitHub stars, AI summary, keywords, upvotes
- **read_paper** — Fetch full paper text as markdown
- **list_daily_papers** — List papers featured on Hugging Face Papers

## Quick Start

```bash
pip install -e ".[dev]"

# stdio mode (for Claude Desktop)
PYTHONPATH=src python3 -m paperwithcode_mcp

# SSE mode (remote access)
PYTHONPATH=src python3 -m paperwithcode_mcp --transport sse --host 127.0.0.1 --port 8787
```

## Environment

- `HTTPS_PROXY` / `HTTP_PROXY` / `ALL_PROXY` — proxy settings (auto-detected)
- `PWC_TIMEOUT` — request timeout in seconds (default: 15.0)

## Claude Desktop Integration

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "paperwithcode": {
      "command": "python3",
      "args": ["-m", "paperwithcode_mcp"],
      "env": {
        "HTTPS_PROXY": "http://127.0.0.1:7890"
      }
    }
  }
}
```

## Development

```bash
python3 -m pytest tests/ -v
```
