from __future__ import annotations

from pathlib import Path


def answer_question(story_path: Path, question: str) -> dict:
    _ = story_path
    return {
        "engine": "nano",
        "question": question,
        "answer": "Placeholder answer from nano GraphRAG.",
        "evidence": "No evidence extraction implemented yet.",
    }
