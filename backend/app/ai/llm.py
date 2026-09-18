import os

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()


client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)


def generate_answer(question: str, context: str):

    prompt = f"""
You are a healthcare assistant.

Answer the user's question using only the healthcare information provided below.

If the information is not available in the provided context, say that you do not have enough information.

Do not provide a diagnosis or replace a healthcare professional.

Healthcare information:
{context}

User question:
{question}
"""

    response = client.responses.create(
        model="openai/gpt-oss-120b",
        input=prompt
    )

    return response.output_text