import asyncio

from app.agent.workflow import healthcare_graph


async def main():

    question = "What appointment slots are available for Dr. Sharma on 30 September 2026?"

    result = await healthcare_graph.ainvoke({
        "messages": [
            {
                "role": "user",
                "content": question
            }
        ],
        "user_id": 2
    })

    print("Question:", question)
    print("\nIntent:", result["intent"])
    print("\nResponse:")
    print(result["response"])


if __name__ == "__main__":
    asyncio.run(main())