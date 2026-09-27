import asyncio

from app.agent.graph import run_agent


async def main():

    answer = await run_agent(
        "I want to book an appointment with Dr. Sharma on 30 September 2026 at 10:00.",
        user_id=2
    )

    print("Agent response:")
    print(answer)


if __name__ == "__main__":
    asyncio.run(main())