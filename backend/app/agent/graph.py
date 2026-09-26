import os
import sys
from pathlib import Path
import time

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.mcp import MCPAdapter
from langchain_groq import ChatGroq
from langchain_core.tools import StructuredTool


load_dotenv()


backend_root = Path(__file__).resolve().parents[2]


MCP_CONFIG = {
    "mcpServers": {
        "odasha": {
            "command": sys.executable,
            "args": [
                "-m",
                "app.mcp.server"
            ],
            "cwd": str(backend_root)
        }
    }
}


async def run_agent(question: str):

    start_time = time.time()

    print("\n--- AGENT START ---")

    model = ChatGroq(
        model="openai/gpt-oss-120b",
        api_key=os.getenv("GROQ_API_KEY")
    )

    async with MCPAdapter(MCP_CONFIG) as adapter:

        mcp_tools = await adapter.list_tools()

        tools = []

        for mcp_tool in mcp_tools:

            async def call_tool(
                _tool=mcp_tool,
                **kwargs
            ):

                result = await _tool.ainvoke(kwargs)

                if isinstance(result, str):
                    return result

                if isinstance(result, list):

                    text_parts = []

                    for item in result:

                        if (
                            isinstance(item, dict)
                            and item.get("type") == "text"
                        ):
                            text_parts.append(
                                item.get("text", "")
                            )
                        else:
                            text_parts.append(
                                str(item)
                            )

                    return "\n".join(text_parts)

                return str(result)

            wrapped_tool = StructuredTool.from_function(
                coroutine=call_tool,
                name=mcp_tool.name,
                description=mcp_tool.description or "",
                args_schema=mcp_tool.args_schema
            )

            tools.append(wrapped_tool)

        print(
            "MCP startup time:",
            round(time.time() - start_time, 2),
            "seconds"
        )

        agent = create_agent(
            model=model,
            tools=tools,
            system_prompt="""
You are Odasha, a healthcare information assistant.

Use the available tools to answer healthcare questions.

For healthcare knowledge questions:
- Use the search_healthcare_knowledge tool.
- Answer ONLY from the information returned by that tool.
- Do not add medical information from your own knowledge.
- Do not invent symptoms, causes, treatments, diagnoses, test values, or recommendations.
- If the tool does not provide enough information, say:
  "I do not have enough information in my healthcare knowledge base."

For doctor-related questions:
- Use the search_doctors tool.
- Only mention doctors returned by the tool.

For appointment questions:
- Use the available appointment tools.
- Do not invent doctors, dates, times, or availability.

Do not provide a diagnosis or replace a healthcare professional.
"""
        )

        result = await agent.ainvoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": question
                    }
                ]
            }
        )

        return result["messages"][-1].content