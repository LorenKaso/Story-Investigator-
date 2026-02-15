from __future__ import annotations

from pathlib import Path

from src.story_loader import load_story_xml


def answer_question(story_path: Path, question: str) -> dict:
    _ = question  # placeholder until RAG is implemented

    messages = load_story_xml(story_path)
    if not messages:
        return {
            "answer": "Not implemented yet (naive_rag).",
            "evidence": [],
            "why_not": "No messages were loaded from the story file.",
        }

    first = messages[0]
    return {
        "answer": "Not implemented yet (naive_rag).",
        "evidence": [{"chunk_id": first.id, "text": first.raw_xml}],
        "why_not": "RAG not implemented yet. Placeholder.",
    }
