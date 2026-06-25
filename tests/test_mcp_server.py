import os
import json

from paperwithcode_mcp.client import PaperPageClient
from paperwithcode_mcp.mcp_server import PapersWithCodeMcpApp
from paperwithcode_mcp import mcp_server


class FakeClient:
    def fetch(self, arxiv_id: str) -> str:
        return '<script>{"githubRepo":"https://github.com/shiyu-coder/Kronos"}</script>'


def test_initialize_and_tools_call():
    app = PapersWithCodeMcpApp(client=FakeClient())

    init_response, session_id = app.handle_jsonrpc(
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2025-03-26",
                "capabilities": {},
                "clientInfo": {"name": "test", "version": "0.1.0"},
            },
        }
    )
    assert session_id is not None

    call_response, _ = app.handle_jsonrpc(
        {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "resolve_code_link",
                "arguments": {"arxiv_id": "2508.02739"},
            },
        }
    )
    payload = json.loads(call_response["result"]["content"][0]["text"])
    assert payload["github_url"] == "https://github.com/shiyu-coder/Kronos"


def test_main_reads_environment_defaults(monkeypatch):
    captured = {}

    class DummyServer:
        def __init__(self, address, handler_class):
            captured["address"] = address
            captured["handler_class"] = handler_class

        def serve_forever(self):
            raise KeyboardInterrupt

        def server_close(self):
            captured["closed"] = True

    monkeypatch.setenv("PWC_BASE_URL", "https://example.com/papers")
    monkeypatch.setenv("PWC_PROXY_URL", "http://proxy.local:7890")
    monkeypatch.setenv("PWC_TIMEOUT", "21.5")
    monkeypatch.setattr(mcp_server, "ThreadingHTTPServer", DummyServer)

    exit_code = mcp_server.main(["--host", "127.0.0.1", "--port", "9999"])

    assert exit_code == 130
    assert captured["address"] == ("127.0.0.1", 9999)
    assert mcp_server._Handler.app.client.base_url == "https://example.com/papers"
    assert mcp_server._Handler.app.client.proxy_url == "http://proxy.local:7890"
    assert mcp_server._Handler.app.client.timeout == 21.5
    assert captured["closed"] is True


def test_client_prefers_standard_proxy_env(monkeypatch):
    monkeypatch.delenv("PWC_PROXY_URL", raising=False)
    monkeypatch.setenv("HTTPS_PROXY", "http://proxy.local:8443")
    client = PaperPageClient()
    assert client._effective_proxy_url() == "http://proxy.local:8443"


def test_client_explicit_proxy_overrides_env(monkeypatch):
    monkeypatch.setenv("HTTPS_PROXY", "http://proxy.local:8443")
    client = PaperPageClient(proxy_url="http://manual.proxy:7890")
    assert client._effective_proxy_url() == "http://manual.proxy:7890"
