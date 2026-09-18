from pathlib import Path
import json

from app.rag.loader import load_knowledge_base
from app.rag.chunker import create_chunks
from app.rag.embedding import create_embeddings
from app.rag.vector_store import create_vector_store, save_vector_store


text = load_knowledge_base()

chunks = create_chunks(text)

embeddings = create_embeddings(chunks)

index = create_vector_store(embeddings)


project_root = Path(__file__).resolve().parents[3]

data_folder = project_root / "data"

vector_store_path = data_folder / "faiss_index.bin"
chunks_path = data_folder / "chunks.json"


save_vector_store(
    index,
    str(vector_store_path)
)

with open(chunks_path, "w", encoding="utf-8") as file:
    json.dump(chunks, file, indent=4)


print("Number of chunks:", len(chunks))
print("Vector store saved successfully.")
print("Chunks saved successfully.")