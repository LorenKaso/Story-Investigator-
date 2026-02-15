from __future__ import annotations

from pathlib import Path


def answer_question(story_path: Path, question: str) -> dict:
    text = story_path.read_text(encoding="utf-8", errors="replace")
    evidence = text[:500]
    return {
        "engine": "naive",
        "question": question,
        "answer": "Placeholder answer from naive RAG.",
        "evidence": evidence,
    }
