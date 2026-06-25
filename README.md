# paperwithcode-mcp

MCP server that provides paper reading and code repository discovery from [Hugging Face Papers](https://huggingface.co/papers). Supports both stdio (Claude Desktop) and SSE (remote) transports.

## Tools

| Tool | Description |
|------|-------------|
| `resolve_code_link` | Resolve an arXiv ID to its GitHub repository URL |
| `get_paper_details` | Get paper metadata: title, authors, abstract, GitHub stars, AI summary, keywords, upvotes |
| `read_paper` | Fetch full paper text as markdown (converted from arXiv HTML) |
| `list_daily_papers` | List papers featured on Hugging Face Papers for a given date |

## Limitations

This project uses **Hugging Face Papers** as its data source, NOT the paperswithcode.com API (which is no longer available). As a result:

- ❌ No paper search by keyword/title
- ❌ No conference/proceedings/author browsing
- ❌ No benchmark results or dataset listings

## Deployment

### pip

```bash
pip install git+https://github.com/GtJerry111/paperwithcode-hf-mcp.git

paperwithcode-mcp  # stdio mode
paperwithcode-mcp --transport sse --host 127.0.0.1 --port 8787  # SSE mode
```

### uv

```bash
uv tool install git+https://github.com/GtJerry111/paperwithcode-hf-mcp.git

paperwithcode-mcp  # stdio mode
```

To update: `uv tool upgrade paperwithcode-mcp`

### Docker

```bash
docker build -t paperwithcode-mcp .
docker run -i --rm paperwithcode-mcp                             # stdio mode
docker run -i --rm -p 8787:8787 paperwithcode-mcp --transport sse --host 0.0.0.0 --port 8787  # SSE mode
```

## Development

```bash
git clone https://github.com/GtJerry111/paperwithcode-hf-mcp.git && cd paperwithcode-hf-mcp

# pip
pip install -e ".[dev]"
pytest tests/ -v

# uv
uv sync --group dev
uv run pytest tests/ -v
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
      "args": []
    }
  }
}
```

If `paperwithcode-mcp` is not found in PATH after pip install, use the full path or:

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

## License

MIT
