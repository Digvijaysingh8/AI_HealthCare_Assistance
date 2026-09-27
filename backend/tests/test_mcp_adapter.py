import asyncio
import sys

from langchain.mcp import MCPAdapter
from pathlib import Path

config = {
    "mcpServers": {
        "odasha": {
            "command": sys.executable,
            "args": [
                "-m",
                "app.mcp.server"
            ],
            "cwd": str(Path.cwd())
        }
    }
}


async def main():

    async with MCPAdapter(config) as adapter:

        tools = await adapter.list_tools()

        search_tool = next(
            tool for tool in tools
            if tool.name == "search_doctors"
        )

        result = await search_tool.ainvoke(
            {
                "specialization": "Cardiology"
            }
        )

        print("Tool result type:")
        print(type(result))

        print("Tool result repr:")
        print(repr(result))

        print("Tool result:")
        print(result)


if __name__ == "__main__":
    asyncio.run(main())