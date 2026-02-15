# Story Investigator (Track A)

This setup provides three runnable systems:

1. `systems/naive_rag.py` (simple chunk + OpenAI embeddings + cosine + LLM)
2. `systems/neo4j_rag.py` (Neo4j GraphRAG package flow)
3. `systems/ms_graphrag.py` (Microsoft GraphRAG CLI wrapper)

## Setup

1. Install dependencies:

```powershell
pip install -r requirements.txt
```

2. Create `.env` from `.env.example` and set at least `OPENAI_API_KEY`.

## Neo4j Docker

Start Neo4j locally:

```powershell
.\scripts\docker_neo4j.ps1
```

View logs:

```powershell
.\scripts\docker_neo4j_logs.ps1
```

Stop Neo4j:

```powershell
.\scripts\docker_neo4j_stop.ps1
```

Neo4j Browser:

- URL: `http://localhost:7474`
- Username: `neo4j`
- Password: `password`

Manual connectivity check:

```powershell
python test_neo4j_connection.py
```

## Run Systems

Naive baseline:

```powershell
python systems/naive_rag.py --story data/story.txt --q "What happened at 09:25?" --topk 5
```

Neo4j GraphRAG index:

```powershell
python systems/neo4j_rag.py --index --story data/story.txt
```

Neo4j GraphRAG query:

```powershell
python systems/neo4j_rag.py --q "What clues mention the vault?" --topk 5
```

Microsoft GraphRAG workspace init:

```powershell
python systems/ms_graphrag.py --init
```

Microsoft GraphRAG index:

```powershell
python systems/ms_graphrag.py --index
```

Microsoft GraphRAG query:

```powershell
python systems/ms_graphrag.py --q "Summarize the core mystery."
```

## Troubleshooting

- If Neo4j connection fails, run `docker ps` and `docker logs neo4j-graphrag`.
- Ensure ports `7474` and `7687` are not already in use.
- Ensure `OPENAI_API_KEY` is set in `.env`.
