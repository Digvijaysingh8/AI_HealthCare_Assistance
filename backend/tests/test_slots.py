import asyncio
import os
import sys

from langchain.mcp import MCPAdapter


config = {
    "mcpServers": {
        "odasha": {
            "command": sys.executable,
            "args": [
                "-m",
                "app.mcp.server"
            ],
            "cwd": os.getcwd()
        }
    }
}


async def main():

    async with MCPAdapter(config) as adapter:

        tools = await adapter.list_tools()

        find_tool = next(
            tool for tool in tools
            if tool.name == "find_doctor"
        )

        result = await find_tool.ainvoke(
            {
                "doctor_name": "Dr. Sharma"
            }
        )

        print("Result:")
        print(result)


if __name__ == "__main__":
    asyncio.run(main())