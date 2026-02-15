from __future__ import annotations

from pathlib import Path

from src.chunker import chunk_messages
from src.gemini_client import GeminiClient
from src.prompt_builder import PromptBuilder, PromptTooLongError
from src.retriever import Embedder, rank_chunks
from src.story_loader import load_story_xml


def answer_question(story_path: Path, question: str) -> dict:
    messages = load_story_xml(story_path)
    chunks = chunk_messages(messages, messages_per_chunk=3)
    ranked = rank_chunks(question, chunks, Embedder())

    top_k = min(4, len(ranked))
    prompt_builder = PromptBuilder()
    selected_chunks = []
    prompt = ""
    if top_k == 0:
        return {
            "answer": "I couldn't answer using Gemini.",
            "evidence": [],
            "why_not": "No chunks available for retrieval.",
        }

    while top_k >= 1:
        selected_chunks = [chunk for chunk, _score in ranked[:top_k]]
        try:
            prompt = prompt_builder.build(
                question, [chunk.text for chunk in selected_chunks]
            )
            break
        except PromptTooLongError:
            top_k -= 1
    else:
        return {
            "answer": "I couldn't answer using Gemini.",
            "evidence": [],
            "why_not": "Prompt too long even with 1 chunk.",
        }

    evidence = [
        {"chunk_id": chunk.chunk_id, "text": chunk.text} for chunk in selected_chunks
    ]
    try:
        gemini_text = GeminiClient().generate(prompt)
    except Exception as exc:
        return {
            "answer": "I couldn't answer using Gemini.",
            "evidence": evidence,
            "why_not": str(exc),
        }

    return {
        "answer": gemini_text,
        "evidence": evidence,
        "why_not": "",
    }
