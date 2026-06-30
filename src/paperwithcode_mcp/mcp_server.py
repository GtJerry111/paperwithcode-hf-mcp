from __future__ import annotations

import json

from mcp.server.fastmcp import FastMCP

from .resolver import (
    get_paper_details,
    list_daily_papers,
    read_paper,
    resolve_code_link,
)

mcp = FastMCP(
    "paperwithcode-mcp",
    instructions="Resolve arXiv paper IDs to GitHub repos and explore papers from Hugging Face Papers.",
)


@mcp.tool(
    description="Resolve an arXiv ID to a GitHub repository URL from the corresponding HF Papers page."
)
async def resolve_code_link_tool(arxiv_id: str) -> str:
    result = resolve_code_link({"arxiv_id": arxiv_id})
    if result is None:
        return json.dumps({"error": "No GitHub repository found"}, ensure_ascii=False)
    return json.dumps(result, ensure_ascii=False)


@mcp.tool(
    description="Get detailed paper metadata including title, authors, abstract, GitHub repo, GitHub stars, AI summary, keywords, and upvotes."
)
async def get_paper_details_tool(arxiv_id: str) -> str:
    data = get_paper_details(arxiv_id)
    if data is None:
        return json.dumps({"error": "Paper not found"}, ensure_ascii=False)
    return json.dumps(
        {
            "id": data.id,
            "title": data.title,
            "authors": data.authors,
            "published_at": data.publishedAt,
            "abstract": data.summary,
            "upvotes": data.upvotes,
            "github_url": data.githubRepo,
            "github_stars": data.githubStars,
            "ai_summary": data.ai_summary,
            "ai_keywords": data.ai_keywords,
        },
        ensure_ascii=False,
    )


@mcp.tool(
    description="Fetch the full text of a paper as markdown."
)
async def read_paper_tool(arxiv_id: str) -> str:
    text = read_paper(arxiv_id)
    if text is None:
        return json.dumps({"error": "Paper content not available"}, ensure_ascii=False)
    return text


@mcp.tool(
    description="List papers featured on Hugging Face Papers for a given date (YYYY-MM-DD format). Defaults to today."
)
async def list_daily_papers_tool(date: str | None = None) -> str:
    papers = list_daily_papers(date)
    return json.dumps(
        [
            {
                "id": p.id,
                "title": p.title,
                "authors": p.authors,
                "summary": p.summary,
                "published_at": p.publishedAt,
                "upvotes": p.upvotes,
                "num_comments": p.numComments,
            }
            for p in papers
        ],
        ensure_ascii=False,
    )


def create_server() -> FastMCP:
    return mcp


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description="HF Papers MCP Server")
    parser.add_argument("--transport", choices=["stdio", "sse", "streamable-http"], default="stdio")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8787)
    args = parser.parse_args(argv)

    mcp.settings.host = args.host
    mcp.settings.port = args.port

    mcp.run(transport=args.transport)
    return 0


def cli() -> None:
    """Console script entry point for `paperwithcode-mcp` command."""
    raise SystemExit(main())


if __name__ == "__main__":
    cli()
