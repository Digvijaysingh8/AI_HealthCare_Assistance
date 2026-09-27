import asyncio
import os
import sys

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.mcp import MCPAdapter
from langchain_groq import ChatGroq


load_dotenv()


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

    model = ChatGroq(
        model="openai/gpt-oss-120b",
        api_key=os.getenv("GROQ_API_KEY")
    )

    async with MCPAdapter(config) as adapter:

        tools = await adapter.list_tools()

        print("MCP tools:")
        for tool in tools:
            print("-", tool.name)

        agent = create_agent(
            model=model,
            tools=tools
        )

        result = await agent.ainvoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": "Find doctors who specialize in Cardiology."
                    }
                ]
            }
        )

        print("\nAgent response:")
        print(result["messages"][-1].content)


if __name__ == "__main__":
    asyncio.run(main())