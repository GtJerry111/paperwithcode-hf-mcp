# paperwithcode_mcp

Standalone MCP service that resolves `arxiv_id -> github_url` from Hugging Face Papers.

## Run locally

```bash
cd /Users/jerry/Projects/paperwithcode_mcp
export HTTPS_PROXY=http://127.0.0.1:7890
export HTTP_PROXY=http://127.0.0.1:7890
PYTHONPATH=src python3 -m paperwithcode_mcp --host 127.0.0.1 --port 8787
```

## Environment

- `PWC_BASE_URL` defaults to `https://huggingface.co/papers`
- `PWC_PROXY_URL` overrides standard proxy env vars when set
- `HTTPS_PROXY` / `HTTP_PROXY` / `ALL_PROXY` are read automatically
- `PWC_TIMEOUT` controls request timeout in seconds

## MCP check

Send `initialize`, then `tools/call` with:

```json
{"arxiv_id":"2508.02739"}
```

Expected result:

```json
{"github_url":"https://github.com/shiyu-coder/Kronos"}
```
