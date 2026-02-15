from __future__ import annotations

import argparse
import os
from pathlib import Path

import numpy as np
from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()


def chunk_text(
    text: str,
    chunk_size: int = 900,
    overlap: int = 180,
) -> list[str]:
    if not text:
        return []
    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size")

    chunks: list[str] = []
    step = chunk_size - overlap
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append(text[start:end])
        if end >= len(text):
            break
        start += step
    return chunks


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    denom = float(np.linalg.norm(a) * np.linalg.norm(b))
    if denom == 0.0:
        return 0.0
    return float(np.dot(a, b) / denom)


def embed_texts(
    client: OpenAI,
    model: str,
    texts: list[str],
) -> list[list[float]]:
    response = client.embeddings.create(model=model, input=texts)
    return [item.embedding for item in response.data]


def build_prompt(question: str, contexts: list[str]) -> str:
    context = "\n\n---\n\n".join(contexts)
    return (
        "You are a story investigator.\n\n"
        f"Question:\n{question}\n\n"
        f"Context:\n{context}\n\n"
        "Answer using only the context above. If insufficient, say so."
    )


def ask_story(
    story_path: Path,
    question: str,
    top_k: int,
    embed_model: str,
    llm_model: str,
) -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY is not set")

    story_text = story_path.read_text(encoding="utf-8")
    chunks = chunk_text(story_text)
    if not chunks:
        return "No story content to search."

    client = OpenAI(api_key=api_key)
    chunk_vectors = embed_texts(client, embed_model, chunks)
    question_vector = embed_texts(client, embed_model, [question])[0]
    question_vec = np.array(question_vector, dtype=float)

    scored: list[tuple[int, float]] = []
    for i, vector in enumerate(chunk_vectors):
        score = cosine_similarity(np.array(vector, dtype=float), question_vec)
        scored.append((i, score))
    scored.sort(key=lambda item: item[1], reverse=True)

    selected = [chunks[i] for i, _ in scored[: max(1, top_k)]]
    prompt = build_prompt(question, selected)

    response = client.chat.completions.create(
        model=llm_model,
        messages=[{"role": "user", "content": prompt}],
    )
    content = response.choices[0].message.content
    return content or "Model returned an empty answer."


def main() -> None:
    parser = argparse.ArgumentParser(description="Naive RAG baseline")
    parser.add_argument("--story", required=True, type=Path)
    parser.add_argument("--q", required=True)
    parser.add_argument("--topk", type=int, default=5)
    args = parser.parse_args()

    embed_model = os.getenv("EMBED_MODEL", "text-embedding-3-small")
    llm_model = os.getenv("LLM_MODEL", "gpt-4o-mini")
    answer = ask_story(args.story, args.q, args.topk, embed_model, llm_model)
    print(answer)


if __name__ == "__main__":
    main()
