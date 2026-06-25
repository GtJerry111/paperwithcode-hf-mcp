FROM python:3.11-slim

# curl is required by the MCP server for HTTP requests
RUN apt-get update && apt-get install -y --no-cache curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY pyproject.toml README.md LICENSE ./
COPY src/ ./src/

RUN pip install --no-cache-dir .

EXPOSE 8787

ENTRYPOINT ["paperwithcode-mcp"]
CMD []
