def create_chunks(text: str):
    chunks = text.split("\n\n\n")

    chunks = [
        chunk.strip()
        for chunk in chunks
        if chunk.strip()
    ]

    return chunks