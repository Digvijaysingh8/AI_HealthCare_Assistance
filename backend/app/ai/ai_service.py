from app.agent.graph import run_agent


async def ask_healthcare_assistant(question: str):

    answer = await run_agent(question)

    return answer