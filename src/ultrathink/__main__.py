from .infrastructure.mcp.server import mcp


def main() -> None:
    """Entry point for the UltraThink MCP server"""
    mcp.run()


if __name__ == "__main__":
    main()
