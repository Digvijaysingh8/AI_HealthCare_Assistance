from app.rag.retriever import retrieve_chunks
from app.ai.llm import generate_answer


question = "What are common symptoms of diabetes?"


results = retrieve_chunks(question)


context = "\n\n".join(results)


answer = generate_answer(
    question,
    context
)


print("\nQuestion:")
print(question)

print("\nRetrieved Context:")
print(context)

print("\nAnswer:")
print(answer)