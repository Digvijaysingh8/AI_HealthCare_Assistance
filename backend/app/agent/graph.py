import os
import sys
from pathlib import Path
import time
from dataclasses import dataclass
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.mcp import MCPAdapter
from langchain_groq import ChatGroq
from langchain_core.tools import StructuredTool


load_dotenv()
@dataclass
class AgentContext:
    user_id: int

backend_root = Path(__file__).resolve().parents[2]

async def run_agent(question: str , user_id: int):

    start_time = time.time()

    print("\n--- AGENT START ---")
    mcp_env = os.environ.copy()
    mcp_env["ODASHA_USER_ID"] = str(user_id)

    MCP_CONFIG = {
        "mcpServers": {
            "odasha": {
                "command": sys.executable,
                "args": [
                    "-m",
                    "app.mcp.server"
                ],
                "cwd": str(backend_root),
                "env": mcp_env
            }
        }
    }

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
            context_schema=AgentContext,
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
- For a new booking request, first use find_doctor if needed.
- Then use get_available_slots to verify the requested date and time.
- Then use prepare_appointment to validate the booking.
- Do NOT call book_appointment during the initial request.
- Ask the user for explicit confirmation before booking.
- Only call book_appointment when the user explicitly confirms the previously prepared booking by saying CONFIRM or an equally clear confirmation.
- Never ask the user for a patient ID. The authenticated patient is determined by the backend.
- If the user's message starts with "CONFIRM_BOOKING:", treat it as explicit confirmation of the appointment described after the colon.
- For a CONFIRM_BOOKING request, do not call prepare_appointment again.
- Extract the doctor, date, and time from the booking request, verify the doctor and slot if necessary, and then call book_appointment with confirmation="CONFIRM".
- After a successful book_appointment result, tell the user the appointment was booked successfully.

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
            },
            context=AgentContext(user_id=user_id)
        )

        return result["messages"][-1].content