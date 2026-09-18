from pathlib import Path


def load_knowledge_base():
    file_path = Path(__file__).resolve().parents[3] / "data" / "healthcare_knowledge.txt"

    with open(file_path, "r", encoding="utf-8") as file:
        text = file.read()

    return text