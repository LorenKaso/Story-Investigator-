from __future__ import annotations

import argparse
import os
from pathlib import Path

from dotenv import load_dotenv
from neo4j import GraphDatabase
from neo4j_graphrag.embeddings import OpenAIEmbeddings
from neo4j_graphrag.generation import GraphRAG
from neo4j_graphrag.indexes import create_vector_index, upsert_vectors
from neo4j_graphrag.llm import OpenAILLM
from neo4j_graphrag.retrievers import VectorRetriever
from neo4j_graphrag.types import EntityType


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


def embedding_dimensions(model_name: str) -> int:
    if model_name == "text-embedding-3-large":
        return 3072
    return 1536


class Neo4jRAG:
    def __init__(self) -> None:
        self.uri = os.getenv("NEO4J_URI", "neo4j://localhost:7687")
        self.username = os.getenv("NEO4J_USERNAME", "neo4j")
        self.password = os.getenv("NEO4J_PASSWORD", "password")
        self.index_name = os.getenv("NEO4J_INDEX_NAME", "story_chunks")
        self.embed_model = os.getenv("EMBED_MODEL", "text-embedding-3-small")
        self.llm_model = os.getenv("LLM_MODEL", "gpt-4o-mini")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY is not set")

    def _driver(self):
        return GraphDatabase.driver(
            self.uri,
            auth=(self.username, self.password),
        )

    def _embedder(self) -> OpenAIEmbeddings:
        return OpenAIEmbeddings(
            model=self.embed_model,
            api_key=self.openai_api_key,
        )

    def index_story(self, story_path: Path) -> None:
        text = story_path.read_text(encoding="utf-8")
        chunks = chunk_text(text)
        if not chunks:
            print("No story content to index.")
            return

        with self._driver() as driver:
            driver.execute_query("MATCH (c:Chunk) DETACH DELETE c")
            create_vector_index(
                driver=driver,
                name=self.index_name,
                label="Chunk",
                embedding_property="embedding",
                dimensions=embedding_dimensions(self.embed_model),
                similarity_fn="euclidean",
                fail_if_exists=False,
            )

            rows = [
                {"id": str(i + 1), "text": chunk}
                for i, chunk in enumerate(chunks)
            ]
            records, _, _ = driver.execute_query(
                "UNWIND $rows AS row "
                "CREATE (c:Chunk {id: row.id, text: row.text}) "
                "RETURN elementId(c) AS element_id, row.text AS text",
                {"rows": rows},
            )
            element_ids = [record["element_id"] for record in records]
            chunk_texts = [record["text"] for record in records]

            embedder = self._embedder()
            embeddings = [
                embedder.embed_query(chunk_text)
                for chunk_text in chunk_texts
            ]
            upsert_vectors(
                driver=driver,
                ids=element_ids,
                embedding_property="embedding",
                embeddings=embeddings,
                entity_type=EntityType.NODE,
            )

        print(
            f"Indexed {len(chunks)} chunk(s) "
            f"into Neo4j index '{self.index_name}'."
        )

    def ask(self, question: str, top_k: int = 5) -> str:
        with self._driver() as driver:
            retriever = VectorRetriever(
                driver=driver,
                index_name=self.index_name,
                embedder=self._embedder(),
                return_properties=["id", "text"],
            )
            llm = OpenAILLM(
                model_name=self.llm_model,
                api_key=self.openai_api_key,
            )
            rag = GraphRAG(retriever=retriever, llm=llm)
            result = rag.search(
                query_text=question,
                retriever_config={"top_k": top_k},
            )
        return result.answer


def main() -> None:
    parser = argparse.ArgumentParser(description="Neo4j GraphRAG system")
    parser.add_argument("--index", action="store_true")
    parser.add_argument("--story", type=Path, default=Path("data/story.txt"))
    parser.add_argument("--q")
    parser.add_argument("--topk", type=int, default=5)
    args = parser.parse_args()

    app = Neo4jRAG()
    if args.index:
        app.index_story(args.story)
        return
    if args.q:
        answer = app.ask(args.q, top_k=args.topk)
        print(answer)
        return
    parser.error("Provide either --index --story <path> or --q \"...\"")


if __name__ == "__main__":
    main()
