from __future__ import annotations

from pathlib import Path


def answer_question(story_path: Path, question: str) -> dict:
    _ = story_path
    return {
        "engine": "ms",
        "question": question,
        "answer": "Placeholder answer from MS GraphRAG.",
        "evidence": "No evidence extraction implemented yet.",
    }
