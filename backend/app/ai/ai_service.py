from app.agent.graph import run_agent


async def ask_healthcare_assistant(
    question: str,
    user_id: int
):

    answer = await run_agent(
        question,
        user_id
    )

    return answer