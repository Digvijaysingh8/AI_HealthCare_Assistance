
import os
import sys
import time
import asyncio
from pathlib import Path
from dataclasses import dataclass
from contextlib import AsyncExitStack

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
def warmup_rag():
    start = time.perf_counter()

    from app.rag.retriever import retrieve_chunks

    retrieve_chunks("healthcare startup warmup")

    print(
        "RAG warmup completed:",
        round(time.perf_counter() - start, 2),
        "seconds",
        flush=True
    )

# Keep one agent and MCP connection per authenticated user.
_agent_cache = {}
_agent_stacks = {}
_agent_locks = {}


SYSTEM_PROMPT = """
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
- Only call book_appointment when the user explicitly confirms
  the previously prepared booking by saying CONFIRM or an
  equally clear confirmation.
- Never ask the user for a patient ID. The authenticated
  patient is determined by the backend.
- If the user's message starts with "CONFIRM_BOOKING:",
  treat it as explicit confirmation of the appointment described
  after the colon.
- For a CONFIRM_BOOKING request, do not call
  prepare_appointment again.
- Extract the doctor, date, and time from the booking request,
  verify the doctor and slot if necessary, and then call
  book_appointment with confirmation="CONFIRM".
- After a successful book_appointment result, tell the user
  the appointment was booked successfully.

Do not provide a diagnosis or replace a healthcare professional.
"""


def get_user_lock(user_id: int):
    if user_id not in _agent_locks:
        _agent_locks[user_id] = asyncio.Lock()

    return _agent_locks[user_id]


async def get_or_create_agent(user_id: int):
    lock = get_user_lock(user_id)

    async with lock:
        if user_id in _agent_cache:
            print(f"Reusing MCP connection for user {user_id}")
            return _agent_cache[user_id]

        print(f"Initializing MCP connection for user {user_id}")
        start_time = time.perf_counter()

        mcp_env = os.environ.copy()
        mcp_env["ODASHA_USER_ID"] = str(user_id)

        mcp_config = {
            "mcpServers": {
                "odasha": {
                    "command": sys.executable,
                    "args": ["-m", "app.mcp.server"],
                    "cwd": str(backend_root),
                    "env": mcp_env,
                }
            }
        }

        model = ChatGroq(
            model="openai/gpt-oss-120b",
            api_key=os.getenv("GROQ_API_KEY"),
        )

        stack = AsyncExitStack()
        await stack.__aenter__()

        try:
            mcp_start = time.perf_counter()

            adapter = await stack.enter_async_context(
                MCPAdapter(mcp_config)
            )

            mcp_tools = await adapter.list_tools()

            tools = []

            for mcp_tool in mcp_tools:
                if mcp_tool.name == "search_healthcare_knowledge":
                    continue

                async def call_tool(_tool=mcp_tool, **kwargs):
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
                                text_parts.append(str(item))

                        return "\n".join(text_parts)

                    return str(result)

                wrapped_tool = StructuredTool.from_function(
                    coroutine=call_tool,
                    name=mcp_tool.name,
                    description=mcp_tool.description or "",
                    args_schema=mcp_tool.args_schema,
                )

                tools.append(wrapped_tool)
            tools.append(
                StructuredTool.from_function(
                    func=search_healthcare_knowledge_local,
                    name="search_healthcare_knowledge",
                    description=(
                        "Search the healthcare knowledge base for "
                        "information relevant to a healthcare question. "
                        "Use this tool for healthcare knowledge queries."
                        ),
                    )
                )
            mcp_time = time.perf_counter() - mcp_start

            agent_start = time.perf_counter()

            agent = create_agent(
                model=model,
                context_schema=AgentContext,
                tools=tools,
                system_prompt=SYSTEM_PROMPT,
            )

            agent_time = time.perf_counter() - agent_start

            _agent_cache[user_id] = agent
            _agent_stacks[user_id] = stack

            print(
                "MCP initialization:",
                round(mcp_time, 2),
                "seconds",
            )
            print(
                "Agent creation:",
                round(agent_time, 2),
                "seconds",
            )
            print(
                "Total initialization:",
                round(time.perf_counter() - start_time, 2),
                "seconds",
            )
            print("MCP tools discovered:", len(tools))

            return agent

        except Exception:
            await stack.aclose()
            raise


async def close_mcp_agents():
    """Close all cached MCP connections during shutdown."""
    stacks = list(_agent_stacks.values())

    _agent_cache.clear()
    _agent_stacks.clear()
    _agent_locks.clear()

    for stack in stacks:
        try:
            await stack.aclose()
        except Exception as error:
            print("Error closing MCP connection:", error)


async def run_agent(question: str, user_id: int):
    request_start = time.perf_counter()

    print("\n--- AGENT START ---")

    agent = await get_or_create_agent(user_id)

    execution_start = time.perf_counter()

    result = await agent.ainvoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": question,
                }
            ]
        },
        context=AgentContext(user_id=user_id),
    )

    execution_time = time.perf_counter() - execution_start
    total_time = time.perf_counter() - request_start

    print(
        "Agent execution:",
        round(execution_time, 2),
        "seconds",
    )
    print(
        "Total request time:",
        round(total_time, 2),
        "seconds",
    )
    print("--- AGENT END ---\n")

    return result["messages"][-1].content

def search_healthcare_knowledge_local(question: str) -> str:
    from app.rag.retriever import retrieve_chunks

    results = retrieve_chunks(question)

    if not results:
        return "No relevant information found in the healthcare knowledge base."

    return "\n".join(str(item) for item in results)
