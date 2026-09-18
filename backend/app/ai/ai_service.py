from app.rag.retriever import retrieve_chunks
from app.ai.llm import generate_answer


def ask_healthcare_assistant(question: str):

    results = retrieve_chunks(question)

    context = "\n\n".join(results)

    answer = generate_answer(
        question,
        context
    )

    return answer