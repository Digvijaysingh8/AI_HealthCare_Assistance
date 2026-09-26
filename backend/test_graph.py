import asyncio

from app.agent.graph import run_agent


async def main():

    answer = await run_agent(
        "What appointment slots are available for Dr. Sharma on 30 September 2026?"
    )

    print("Agent response:")
    print(answer)


if __name__ == "__main__":
    asyncio.run(main())