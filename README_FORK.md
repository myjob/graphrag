
# GraphRAG Fork: Postgres Vector Store & Chunk Injection

This repository contains a customized version of GraphRAG configured to:
1.  Use **Postgres (pgvector)** as the vector store.
2.  **Inject existing chunks** from Postgres, bypassing the default text splitting pipeline.
3.  Use **Ollama** for local LLM inference.

## Key Features

*   **Custom Vector Store**: Implemented `PostgresVectorStore` in `src/graphrag/vector_stores/postgres.py`.
*   **Injection Script**: `scripts/inject_postgres_chunks.py` fetches chunks from your Postgres table and focuses them into `text_units.parquet` and `documents.parquet` for GraphRAG.
*   **Custom Workflow**: `docs/settings.yaml` is configured to skip ingestion and start directly from `create_final_documents`.

## Setup

1.  **Environment**: Ensure `.env` contains your Postgres credentials (`DB_HOST`, `DB_NAME`, etc.) and `GRAPHRAG_CHAT_MODEL`.
2.  **Configurations**: Check `docs/settings.yaml` for:
    *   `vector_store.type: postgres`
    *   `workflows`: Explicit list starting with `create_final_documents`.
    *   `request_timeout`: Increased to allow for Ollama model loading.

## Usage

### 1. Inject Data
Run the injection script to pull chunks from your usage-specific Postgres table and generate the required input Parquet files.
```bash
python scripts/inject_postgres_chunks.py
```
*   *Note*: Update `TABLE_NAME` and column mappings in the script before running.

### 2. Run Pipeline
Use the `run_graphrag.py` helper script (which patches the CLI to use the local source code) to execute the indexing pipeline.
```bash
# Set PYTHONPATH to src to ensure local changes are used
PYTHONPATH=src python run_graphrag.py index --root ./docs --verbose
```
