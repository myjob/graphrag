
pyenv local 3.12

https://microsoft.github.io/graphrag/get_started/
pip install graphrag

graphrag index --root ./

graphrag query --root ./docs --method local --query "BRITTAN"
graphrag query --root ./docs --method local --query "when was the decision taken?"
graphrag query --root ./docs --method drift --query "when was the decision taken?"
graphrag index --root ./docs


git clone https://github.com/noworneverev/graphrag-visualizer.git
cd graphrag-visualizer
npm install
npm start

---------------
## VIBE
---------------
settings.yaml added pgvector and ollama LLM with timeout 10m

---------------
lets assume the vector db contains already text chunks and embeddings: would it possible to build the knowledge graph by leveraging the given vector db content?
Short Answer: Not directly out-of-the-box, but possible with a workaround.

GraphRAG's indexing pipeline expects to go through a specific flow: Documents -> Text Units -> Graph Extraction -> Communities -> Reports.

If your vector DB already has the text chunks:

Skip Chunking: You can write a script to query your vector DB for all text chunks and save them as a CSV or Parquet file.
Inject into Pipeline: You can format this data to match GraphRAG's input schema or output/text_units.parquet schema.
Build Graph: Run the graph extraction and clustering steps using this input.
Leveraging Existing Embeddings: This is harder. GraphRAG generates embeddings for new things it creates (like Community Reports and Entity Descriptions). It could potentially reuse document embeddings if you match the IDs and schema perfectly, but GraphRAG usually calculates these as part of its own generate_text_embeddings workflow. The most practical approach is to reuse the text to build the graph, but let GraphRAG manage the embedding space to ensure consistency with its graph traversal mechanisms.

The cleanest way to "intercept" the splitter is to bypass it entirely.

GraphRAG's indexing process is a chain of workflows that produce intermediate Parquet files in the output directory.

load_input_documents -> documents.parquet
create_base_text_units (The Splitter) -> text_units.parquet
extract_graph (The LLM) -> Reads text_units.parquet
The Strategy:

Extract & Format: Write a Python script to query your pgvector table for the chunks.
Mock the Artifact: certain columns are required (id, text, document_ids, n_tokens). Format your data into a Pandas DataFrame matching this schema.
Inject: Save this DataFrame as output/text_units.parquet.
Run: You can then run the remaining GraphRAG workflows. (Standard CLI might try to overwrite it, so you might need to use the Python API or careful resume flags, but injection is the key).
pyenv local 3.12

https://microsoft.github.io/graphrag/get_started/
pip install graphrag

graphrag index --root ./

graphrag query --root ./docs --method local --query "BRITTAN"
graphrag query --root ./docs --method local --query "when was the decision taken?"
graphrag query --root ./docs --method drift --query "when was the decision taken?"
graphrag index --root ./docs


git clone https://github.com/noworneverev/graphrag-visualizer.git
cd graphrag-visualizer
npm install
npm start

---------------
## VIBE
---------------
settings.yaml added pgvector and ollama LLM with timeout 10m

---------------
lets assume the vector db contains already text chunks and embeddings: would it possible to build the knowledge graph by leveraging the given vector db content?
Short Answer: Not directly out-of-the-box, but possible with a workaround.

GraphRAG's indexing pipeline expects to go through a specific flow: Documents -> Text Units -> Graph Extraction -> Communities -> Reports.

If your vector DB already has the text chunks:

Skip Chunking: You can write a script to query your vector DB for all text chunks and save them as a CSV or Parquet file.
Inject into Pipeline: You can format this data to match GraphRAG's input schema or output/text_units.parquet schema.
Build Graph: Run the graph extraction and clustering steps using this input.
Leveraging Existing Embeddings: This is harder. GraphRAG generates embeddings for new things it creates (like Community Reports and Entity Descriptions). It could potentially reuse document embeddings if you match the IDs and schema perfectly, but GraphRAG usually calculates these as part of its own generate_text_embeddings workflow. The most practical approach is to reuse the text to build the graph, but let GraphRAG manage the embedding space to ensure consistency with its graph traversal mechanisms.

The cleanest way to "intercept" the splitter is to bypass it entirely.

GraphRAG's indexing process is a chain of workflows that produce intermediate Parquet files in the output directory.

load_input_documents -> documents.parquet
create_base_text_units (The Splitter) -> text_units.parquet
extract_graph (The LLM) -> Reads text_units.parquet
The Strategy:

Extract & Format: Write a Python script to query your pgvector table for the chunks.
Mock the Artifact: certain columns are required (id, text, document_ids, n_tokens). Format your data into a Pandas DataFrame matching this schema.
Inject: Save this DataFrame as output/text_units.parquet.
Run: You can then run the remaining GraphRAG workflows. (Standard CLI might try to overwrite it, so you might need to use the Python API or careful resume flags, but injection is the key).
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
