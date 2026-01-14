"""
Main entry point for the Graph Mail MCP Server
"""

import asyncio
from .server import main

if __name__ == "__main__":
    asyncio.run(main())
