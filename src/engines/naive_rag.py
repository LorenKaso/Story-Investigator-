from __future__ import annotations

from pathlib import Path

from src.chunker import chunk_messages
from src.story_loader import load_story_xml


def answer_question(story_path: Path, question: str) -> dict:
    _ = question
    messages = load_story_xml(story_path)
    chunks = chunk_messages(messages, messages_per_chunk=2)
    evidence = []
    if chunks:
        chunk = chunks[0]
        evidence = [{"chunk_id": chunk.chunk_id, "text": chunk.text}]

    return {
        "answer": "Not implemented yet (naive_rag).",
        "evidence": evidence,
        "why_not": "RAG not implemented yet. Placeholder.",
    }
