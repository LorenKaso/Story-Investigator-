from __future__ import annotations

import argparse
from pathlib import Path

from engines import ms_graphrag_rag, naive_rag, nano_graphrag_rag


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="AI Investigator CLI")
    parser.add_argument("--story", required=True, help="Path to story file")
    parser.add_argument(
        "--engine",
        choices=("naive", "nano", "ms"),
        default="naive",
        help="RAG engine to use",
    )
    return parser.parse_args()


def select_engine(engine_name: str):
    if engine_name == "naive":
        return naive_rag.answer_question
    if engine_name == "nano":
        return nano_graphrag_rag.answer_question
    return ms_graphrag_rag.answer_question


def main() -> None:
    args = parse_args()
    story_path = Path(args.story)
    answer_fn = select_engine(args.engine)

    print("AI Investigator 1.0. Ask me any question about the story")

    while True:
        try:
            question = input("> ").strip()
        except KeyboardInterrupt:
            print("\nExiting.")
            break

        if question.lower() == "exit":
            print("Exiting.")
            break
        if not question:
            continue

        result = answer_fn(story_path, question)
        print(result)


if __name__ == "__main__":
    main()
