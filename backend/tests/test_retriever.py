"""Tests for lexical knowledge-base retrieval.

Retrieval used to be embedding-based. These cases pin the behaviour that the
assistant prompt depends on: a question about a condition returns that
condition's section, and an unrelated question returns nothing so the model can
say it lacks the information.
"""

import pytest

from app.rag.retriever import retrieve_chunks


def title_of(chunk: str) -> str:
    """The first line of a chunk names the condition."""
    return chunk.splitlines()[0]


# Questions phrased several different ways per condition, matching how patients
# actually ask rather than how the knowledge base is written.
MATCHES = [
    ("What are common symptoms of Asthma?", "Asthma"),
    ("What causes asthma?", "Asthma"),
    ("chest tightness and wheezing", "Asthma"),
    ("Shortness of breath when exercising", "Asthma"),
    ("asthma attack", "Asthma"),

    ("symptoms of dengue", "Dengue"),
    ("Dengue fever symptoms", "Dengue"),
    ("Is dengue contagious?", "Dengue"),
    ("fever with joint pain and rash", "Dengue"),
    ("fever and rash after mosquito bite", "Dengue"),

    ("How do I know if I have diabetes?", "Diabetes"),
    ("What are the symptoms of diabetes mellitus?", "Diabetes"),
    ("Tell me about blood sugar problems", "Diabetes"),
    ("my blood sugar is high", "Diabetes"),
    ("sugar level check", "Diabetes"),
    ("how is diabetes treated", "Diabetes"),

    ("What is high blood pressure?", "Hypertension"),
    ("high blood pressure", "Hypertension"),
    ("Treatment for hypertension", "Hypertension"),
    ("How is hypertension diagnosed?", "Hypertension"),
    ("high bp", "Hypertension"),
    ("tell me about hypertension", "Hypertension"),

    ("I have a runny nose and sore throat, what is it?", "Common Cold"),
    ("What should I do about a common cold?", "Common Cold"),
    ("sore throat and cough", "Common Cold"),
    ("runny nose", "Common Cold"),
    ("is the common cold viral", "Common Cold"),
]


@pytest.mark.parametrize("question,expected", MATCHES)
def test_returns_the_matching_condition(question, expected):
    results = retrieve_chunks(question)

    assert results, f"expected a match for {question!r}"
    assert title_of(results[0]) == expected


# Questions sharing only an incidental word with a section, or nothing at all.
# Returning a chunk here would invite the model to answer from irrelevant text.
NO_MATCHES = [
    "",
    "   ",
    "!!! ???",
    "xyzzy plugh",
    "What is the capital of France?",
    "Who won the 2022 World Cup?",
    "How do I reset my password?",
    "What is the stock price of Apple?",
    "Can you write me a poem",
    "Tell me a joke",
    "What time is it",
    "Book me an appointment with Dr Smith",
    # Conditions the knowledge base does not cover.
    "What about cancer?",
    "Tell me about tuberculosis",
    # These share a symptom word with a section but are not that condition.
    "migraine headaches",
    "I have a headache",
    "back pain",
]


@pytest.mark.parametrize("question", NO_MATCHES)
def test_unrelated_questions_return_nothing(question):
    assert retrieve_chunks(question) == []


def test_knowledge_base_is_loaded():
    """A silently empty index would look identical to 'no match'."""
    results = retrieve_chunks("symptoms of diabetes")

    assert len(results) == 1
    assert "diabetes" in results[0].lower()


def test_top_k_controls_result_count():
    results = retrieve_chunks("fever rash joint pain", top_k=2)

    assert 1 <= len(results) <= 2


def test_results_are_stable_across_calls():
    first = retrieve_chunks("symptoms of dengue", top_k=3)
    second = retrieve_chunks("symptoms of dengue", top_k=3)

    assert first == second