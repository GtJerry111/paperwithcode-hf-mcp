from __future__ import annotations

import argparse
import json
import os
import uuid
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from .client import PaperPageClient
from .resolver import resolve_code_link


def _tool_schema() -> dict:
    return {
        "name": "resolve_code_link",
        "description": "Resolve an arXiv ID to a GitHub repository URL from the corresponding paper page.",
        "inputSchema": {
            "type": "object",
            "properties": {"arxiv_id": {"type": "string"}},
            "required": ["arxiv_id"],
            "additionalProperties": False,
        },
    }


class PapersWithCodeMcpApp:
    def __init__(self, client: PaperPageClient | None = None):
        self.client = client or PaperPageClient()

    def handle_jsonrpc(self, payload: dict) -> tuple[dict, str | None]:
        method = payload.get("method")
        request_id = payload.get("id")

        if method == "initialize":
            return (
                {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "protocolVersion": "2025-03-26",
                        "serverInfo": {"name": "paperwithcode-mcp", "version": "0.1.0"},
                        "capabilities": {"tools": {}},
                    },
                },
                str(uuid.uuid4()),
            )

        if method == "tools/list":
            return (
                {"jsonrpc": "2.0", "id": request_id, "result": {"tools": [_tool_schema()]}},
                None,
            )

        if method == "tools/call":
            params = payload.get("params") or {}
            if params.get("name") != "resolve_code_link":
                return ({"jsonrpc": "2.0", "id": request_id, "error": {"code": -32601, "message": "Unknown tool"}}, None)
            result = resolve_code_link(params.get("arguments") or {}, client=self.client)
            return (
                {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [{"type": "text", "text": json.dumps(result, ensure_ascii=False)}],
                        "structuredContent": result,
                    },
                },
                None,
            )

        return ({"jsonrpc": "2.0", "id": request_id, "error": {"code": -32601, "message": "Unsupported method"}}, None)


class _Handler(BaseHTTPRequestHandler):
    app: PapersWithCodeMcpApp

    def do_GET(self) -> None:  # noqa: N802
        if self.path != "/health":
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(b"ok")

    def do_POST(self) -> None:  # noqa: N802
        if self.path != "/mcp":
            self.send_error(HTTPStatus.NOT_FOUND)
            return

        length = int(self.headers.get("Content-Length", "0"))
        payload = json.loads(self.rfile.read(length) or b"{}")
        response, session_id = self.app.handle_jsonrpc(payload)

        body = "data: " + json.dumps(response, ensure_ascii=False) + "\n\n"
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "text/event-stream; charset=utf-8")
        self.send_header("Cache-Control", "no-cache")
        if session_id:
            self.send_header("mcp-session-id", session_id)
        self.end_headers()
        self.wfile.write(body.encode("utf-8"))

    def log_message(self, format: str, *args) -> None:  # noqa: A003
        return


def main(argv: list[str] | None = None) -> int:
    env_base_url = os.getenv("PWC_BASE_URL", "https://huggingface.co/papers")
    env_proxy_url = os.getenv("PWC_PROXY_URL")
    env_timeout = float(os.getenv("PWC_TIMEOUT", "15.0"))

    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8787)
    parser.add_argument("--base-url", default=env_base_url)
    parser.add_argument("--proxy-url", default=env_proxy_url)
    parser.add_argument("--timeout", type=float, default=env_timeout)
    args = parser.parse_args(argv)

    client = PaperPageClient(base_url=args.base_url, proxy_url=args.proxy_url, timeout=args.timeout)
    _Handler.app = PapersWithCodeMcpApp(client=client)
    server = ThreadingHTTPServer((args.host, args.port), _Handler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        return 130
    finally:
        server.server_close()
    return 0
