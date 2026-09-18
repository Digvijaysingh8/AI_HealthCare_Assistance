from pathlib import Path
import json

from app.rag.embedding import model
from app.rag.vector_store import load_vector_store


project_root = Path(__file__).resolve().parents[3]

vector_store_path = project_root / "data" / "faiss_index.bin"
chunks_path = project_root / "data" / "chunks.json"


index = load_vector_store(str(vector_store_path))

with open(chunks_path, "r", encoding="utf-8") as file:
    chunks = json.load(file)


def retrieve_chunks(question: str, top_k: int = 1):
    question_embedding = model.encode([question])

    distances, indices = index.search(
        question_embedding,
        top_k
    )

    results = []

    for index_value in indices[0]:
        results.append(chunks[index_value])

    return results