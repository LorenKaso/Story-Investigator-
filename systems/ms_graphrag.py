from __future__ import annotations

import argparse
import shutil
import subprocess
from pathlib import Path


WORKSPACE_ROOT = Path("ms_graphrag_workspace")
INPUT_DIR = WORKSPACE_ROOT / "input"
DEFAULT_STORY = Path("data/story.txt")


def run_command(command: list[str], title: str) -> None:
    print(f"[ms_graphrag] {title}")
    subprocess.run(command, check=True)


def init_workspace() -> None:
    WORKSPACE_ROOT.mkdir(parents=True, exist_ok=True)
    run_command(
        ["graphrag", "init", "--root", str(WORKSPACE_ROOT), "--force"],
        "Initializing workspace",
    )


def copy_story(story_path: Path) -> None:
    INPUT_DIR.mkdir(parents=True, exist_ok=True)
    destination = INPUT_DIR / story_path.name
    shutil.copy2(story_path, destination)
    print(f"[ms_graphrag] Copied story to {destination}")


def build_index(story_path: Path) -> None:
    copy_story(story_path)
    run_command(
        ["graphrag", "index", "--root", str(WORKSPACE_ROOT)],
        "Building index",
    )


def query(question: str) -> None:
    run_command(
        ["graphrag", "query", "--root", str(WORKSPACE_ROOT), question],
        "Running query",
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Microsoft GraphRAG CLI wrapper"
    )
    parser.add_argument("--init", action="store_true")
    parser.add_argument("--index", action="store_true")
    parser.add_argument("--story", type=Path, default=DEFAULT_STORY)
    parser.add_argument("--q")
    args = parser.parse_args()

    if args.init:
        init_workspace()
        return
    if args.index:
        build_index(args.story)
        return
    if args.q:
        query(args.q)
        return
    parser.error("Provide one of: --init, --index, or --q \"...\"")


if __name__ == "__main__":
    main()
