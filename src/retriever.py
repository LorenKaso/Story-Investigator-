from __future__ import annotations

from math import sqrt
from typing import Any

from sentence_transformers import SentenceTransformer

from src.chunker import Chunk


class Embedder:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2") -> None:
        self._model: Any = SentenceTransformer(model_name)

    def embed(self, texts: list[str]) -> list[list[float]]:
        vectors = self._model.encode(texts)
        return [list(vector) for vector in vectors]


def cosine_similarity(a: list[float], b: list[float]) -> float:
    if len(a) != len(b) or not a:
        return 0.0

    dot = sum(x * y for x, y in zip(a, b))
    norm_a = sqrt(sum(x * x for x in a))
    norm_b = sqrt(sum(y * y for y in b))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return dot / (norm_a * norm_b)


def rank_chunks(
    question: str, chunks: list[Chunk], embedder: Embedder
) -> list[tuple[Chunk, float]]:
    if not chunks:
        return []

    question_embedding = embedder.embed([question])[0]
    chunk_embeddings = embedder.embed([chunk.text for chunk in chunks])

    ranked = [
        (chunk, cosine_similarity(question_embedding, embedding))
        for chunk, embedding in zip(chunks, chunk_embeddings)
    ]
    ranked.sort(key=lambda item: item[1], reverse=True)
    return ranked
