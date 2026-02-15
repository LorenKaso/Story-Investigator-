from __future__ import annotations

from dataclasses import dataclass

from src.story_loader import Message


@dataclass
class Chunk:
    chunk_id: int
    message_ids: list[str]
    text: str


def chunk_messages(messages: list[Message], messages_per_chunk: int = 3) -> list[Chunk]:
    chunks: list[Chunk] = []
    for i in range(0, len(messages), messages_per_chunk):
        batch = messages[i : i + messages_per_chunk]
        chunks.append(
            Chunk(
                chunk_id=len(chunks),
                message_ids=[m.id for m in batch],
                text="\n\n".join(m.raw_xml for m in batch),
            )
        )
    return chunks
