"""Allow running as `python -m skyportal_mcp` or via the `skyportal-mcp` CLI."""

import os

from .server import MCP_HOST, MCP_PORT, logger, mcp


def main():
    transport = os.getenv("MCP_TRANSPORT", "stdio")
    if transport == "stdio":
        logger.info("Starting MCP server in stdio mode")
        mcp.run(transport="stdio", show_banner=False)
    elif transport == "http":
        logger.info("Starting MCP server in HTTP mode on %s:%s", MCP_HOST, MCP_PORT)
        mcp.run(
            transport="http",
            host=MCP_HOST,
            port=MCP_PORT,
            show_banner=True,
        )
    else:
        raise ValueError(f"Unknown transport: {transport}. Use 'stdio' or 'http'.")


if __name__ == "__main__":
    main()
