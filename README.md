# paperwithcode_mcp

MCP server that provides paper reading and code repository discovery from [Hugging Face Papers](https://huggingface.co/papers). Supports both stdio (Claude Desktop) and SSE (remote) transports.

## Features

| Tool | Description |
|------|-------------|
| `resolve_code_link` | Resolve an arXiv ID to its GitHub repository URL |
| `get_paper_details` | Get paper metadata: title, authors, abstract, GitHub stars, AI summary, keywords, upvotes |
| `read_paper` | Fetch full paper text as markdown (converted from arXiv HTML) |
| `list_daily_papers` | List papers featured on Hugging Face Papers for a given date |

## Limitations

This project uses **Hugging Face Papers** as its data source, NOT the paperswithcode.com API (which is no longer available). As a result:

- ❌ No paper search by keyword/title — HF Papers doesn't provide a public search API
- ❌ No conference/proceedings/author browsing
- ❌ No benchmark results, dataset listings, or research area taxonomy

If you need those features, this is not the right tool.

## Requirements

- Python >= 3.11
- `curl` — installed system-wide (used internally for HTTP requests)

## Installation

```bash
pip install git+https://github.com/jerry/paperwithcode-mcp.git

# stdio mode (for Claude Desktop)
paperwithcode-mcp

# SSE mode (remote access)
paperwithcode-mcp --transport sse --host 127.0.0.1 --port 8787
```

### Development install

```bash
git clone <repo-url>
cd paperwithcode-mcp
pip install -e ".[dev]"
python3 -m pytest tests/ -v

# Run server from source
PYTHONPATH=src python3 -m paperwithcode_mcp
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
      "command": "paperwithcode-mcp",
      "args": [],
      "env": {
        "HTTPS_PROXY": "http://127.0.0.1:7890"
      }
    }
  }
}
```

> Note: If `paperwithcode-mcp` is not found in PATH after pip install, use the full path: `"command": "python3", "args": ["-m", "paperwithcode_mcp"]`

## Docker

```bash
docker build -t paperwithcode-mcp .
docker run -i --rm paperwithcode-mcp  # stdio mode
docker run -i --rm -p 8787:8787 paperwithcode-mcp --transport sse --host 0.0.0.0 --port 8787
```

## License

MIT
