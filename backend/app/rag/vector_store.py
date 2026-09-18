import faiss
import numpy as np


def create_vector_store(embeddings):
    embeddings = np.array(embeddings).astype("float32")

    dimension = embeddings.shape[1]

    index = faiss.IndexFlatL2(dimension)

    index.add(embeddings)

    return index


def save_vector_store(index, file_path):
    faiss.write_index(index, file_path)


def load_vector_store(file_path):
    return faiss.read_index(file_path)