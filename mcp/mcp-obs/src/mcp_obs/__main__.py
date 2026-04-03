"""Allow running as `python -m mcp_obs`."""

from .server import mcp

if __name__ == "__main__":
    mcp.run()
