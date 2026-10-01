"""Lexical retrieval over the healthcare knowledge base.

The knowledge base is a handful of short paragraphs, one per condition, so the
chunks are scored directly with BM25 over their tokens. This replaced a
sentence-transformers + FAISS pipeline that needed roughly 460 MB of PyTorch
for the same job, which is what pushed the container past its memory cap.

`healthcare_knowledge.txt` is the single source of truth: the text is chunked
and indexed at import time, so editing the file is all that is needed to change
what the assistant knows. No index rebuild step is required.
"""

import math
import re

from app.rag.chunker import create_chunks
from app.rag.loader import load_knowledge_base


# BM25 tuning. b=0.75 is the standard default and suits chunks of similar
# length; k1=1.5 stops a repeated term from dominating the score.
_BM25_K1 = 1.5
_BM25_B = 0.75

# Title tokens (the first line of a chunk, which names the condition) count for
# more than body tokens. A question naming a condition should land on that
# chunk even when the rest of the wording differs.
_TITLE_BOOST = 2.5

# Phrases that carry the intent of a chunk without appearing in it verbatim.
# The knowledge base is written in clinical wording, and patients ask in lay
# wording, so these bridge the two for the handful of terms that matter.
# Each entry lists the tokens to add to the query.
_ALIASES = {
    "blood sugar": ["glucose", "diabetes"],
    "sugar level": ["glucose", "diabetes"],
    "high sugar": ["glucose", "diabetes"],
    "insulin": ["glucose", "diabetes"],
    "bp": ["pressure", "hypertension"],
    "mosquito": ["dengue", "mosquitoes"],
    "itchy throat": ["sore", "throat"],
    "blocked nose": ["runny", "nose"],
    "breathless": ["breath", "shortness"],
    "cannot breathe": ["breathing", "airways"],
    "skin rash": ["rash"],
    "high temperature": ["fever"],
}


# Words that carry no retrieval signal. Kept small and English-only: a longer
# list would strip meaningful terms from short medical questions.
_STOPWORDS = frozenset(
    """
    a about all also am an and any are as at be because been but by can could
    do does doing for from get got had has have how i if in into is it its me
    my of on or our out should so some than that the their them then there
    these they this to up us was we were what when where which who why will
    with would you your
    """.split()
)

_TOKEN_RE = re.compile(r"[a-z0-9]+")


def _tokenize(text: str) -> list[str]:
    """Lowercase, split on non-alphanumerics, drop stopwords, fold plurals."""
    tokens = []

    for token in _TOKEN_RE.findall(text.lower()):
        if token in _STOPWORDS:
            continue

        # Fold plurals so "symptoms" and "symptom" match. Left alone when the
        # word ends in "ss" or "us" so "stress" and "virus" survive.
        if (
            len(token) > 3
            and token.endswith("s")
            and not token.endswith("ss")
            and not token.endswith("us")
        ):
            token = token[:-1]

        tokens.append(token)

    return tokens


def _expand_query(question: str) -> list[str]:
    """Tokenize the question, then add tokens for any alias phrases in it."""
    tokens = _tokenize(question)

    lowered = question.lower()

    for phrase, extra in _ALIASES.items():
        if phrase in lowered:
            # Alias terms go through the tokenizer too, otherwise an entry like
            # "diabetes" would miss a chunk whose text folded to "diabete".
            tokens.extend(_tokenize(" ".join(extra)))

    return tokens


class _Chunk:
    """One knowledge-base section, pre-scored for BM25."""

    def __init__(self, text: str):
        self.text = text

        lines = text.splitlines()
        title = lines[0] if lines else ""

        body_tokens = _tokenize(text)
        title_tokens = _tokenize(title)

        self.term_frequencies = {}
        for token in body_tokens:
            self.term_frequencies[token] = (
                self.term_frequencies.get(token, 0) + 1
            )

        # Title terms are added on top of the body counts rather than counted
        # separately, so a title hit boosts an existing term and introduces a
        # title-only term at the boosted weight.
        for token in title_tokens:
            self.term_frequencies[token] = (
                self.term_frequencies.get(token, 0) + _TITLE_BOOST
            )

        self.length = sum(self.term_frequencies.values())

    def score(
        self,
        query_tokens: list[str],
        idf: dict,
        average_length: float,
    ) -> float:
        if not self.length:
            return 0.0

        total = 0.0

        for token in set(query_tokens):
            frequency = self.term_frequencies.get(token)
            if not frequency:
                continue

            weight = idf.get(token)
            if weight is None:
                continue

            denominator = frequency + _BM25_K1 * (
                1 - _BM25_B + _BM25_B * self.length / average_length
            )

            total += weight * (
                frequency * (_BM25_K1 + 1) / denominator
            )

        return total


def _build_index(text: str) -> list[_Chunk]:
    return [_Chunk(chunk) for chunk in create_chunks(text)]


_chunks = _build_index(load_knowledge_base())

_average_length = (
    sum(chunk.length for chunk in _chunks) / len(_chunks) or 1
)

# How many chunks contain each term, used for the inverse document frequency.
_document_frequency = {}

for _chunk in _chunks:
    for _token in _chunk.term_frequencies:
        _document_frequency[_token] = (
            _document_frequency.get(_token, 0) + 1
        )

_chunk_count = len(_chunks)

_idf = {
    token: math.log(
        1 + (_chunk_count - frequency + 0.5) / (frequency + 0.5)
    )
    for token, frequency in _document_frequency.items()
}


# Score floor below which a match is not trusted.
#
# Measured against the knowledge base, questions that name a condition or its
# symptoms score 2.6 and above, while questions with only an incidental word in
# common ("migraine headaches" matching on "headache", "back pain" matching on
# "pain") score 1.5 and below. 2.0 sits in that gap.
#
# Returning nothing for an unrelated question is the intended behaviour: the
# system prompt tells the assistant to say it lacks the information rather than
# invent it, and a spurious chunk would work against that. Raise this only
# alongside a re-measurement of both groups.
_MIN_SCORE = 2.0


def retrieve_chunks(question: str, top_k: int = 1) -> list[str]:
    """Return the best matching knowledge-base sections, best first."""
    query_tokens = _expand_query(question)

    if not query_tokens:
        return []

    scored = [
        (chunk.score(query_tokens, _idf, _average_length), chunk.text)
        for chunk in _chunks
    ]

    scored = [item for item in scored if item[0] >= _MIN_SCORE]

    if not scored:
        return []

    # Ties are broken by chunk order so results stay stable between calls.
    scored.sort(key=lambda item: -item[0])

    return [text for _, text in scored[:top_k]]