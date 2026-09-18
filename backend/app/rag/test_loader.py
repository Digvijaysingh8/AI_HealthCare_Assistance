from app.rag.retriever import retrieve_chunks


question = "What are common symptoms of Asthma?"

results = retrieve_chunks(question)

print("\nQuestion:")
print(question)

print("\nRetrieved information:")

for result in results:
    print(result)