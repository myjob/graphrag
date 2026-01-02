# Copyright (c) 2024 Microsoft Corporation.
# Licensed under the MIT License

"""Postgres vector storage implementation."""

import json
import os
from typing import Any

import numpy as np
from graphrag.config.models.vector_store_schema_config import VectorStoreSchemaConfig
from graphrag.data_model.types import TextEmbedder
from graphrag.vector_stores.base import (
    BaseVectorStore,
    VectorStoreDocument,
    VectorStoreSearchResult,
)


class PostgresVectorStore(BaseVectorStore):
    """Postgres vector storage implementation."""

    def __init__(
        self, vector_store_schema_config: VectorStoreSchemaConfig, **kwargs: Any
    ) -> None:
        super().__init__(
            vector_store_schema_config=vector_store_schema_config, **kwargs
        )
        self.db_connection = None
        self.cursor = None

    def connect(self, **kwargs: Any) -> Any:
        """Connect to the vector storage."""
        import psycopg2

        self.db_connection = psycopg2.connect(
            dbname=os.getenv("DB_NAME", "agno_play"),
            user=os.getenv("DB_USER", "ai"),
            password=os.getenv("DB_PASSWORD", "ai"),
            host=os.getenv("DB_HOST", "localhost"),
            port=os.getenv("DB_PORT", "5433"),
        )
        self.cursor = self.db_connection.cursor()
        # Enable vector extension
        self.cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        self.db_connection.commit()

    def load_documents(
        self, documents: list[VectorStoreDocument], overwrite: bool = True
    ) -> None:
        """Load documents into vector storage."""
        if not documents:
            return

        table_name = self.index_name
        # Assuming vector size is consistent
        dim = len(documents[0].vector) if documents[0].vector else 1536

        # Drop table if overwrite
        if overwrite:
            self.cursor.execute(f"DROP TABLE IF EXISTS {table_name}")

        # Create table
        self.cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                id TEXT PRIMARY KEY,
                text TEXT,
                attributes JSONB,
                vector vector({dim})
            )
        """)

        # Upsert
        from psycopg2.extras import execute_values

        data = []
        for doc in documents:
            if doc.vector:
                data.append((doc.id, doc.text, json.dumps(doc.attributes), doc.vector))

        insert_query = f"""
            INSERT INTO {table_name} (id, text, attributes, vector)
            VALUES %s
            ON CONFLICT (id) DO UPDATE SET
                text = EXCLUDED.text,
                attributes = EXCLUDED.attributes,
                vector = EXCLUDED.vector
        """
        execute_values(self.cursor, insert_query, data)
        self.db_connection.commit()

    def filter_by_id(self, include_ids: list[str] | list[int]) -> Any:
        """Build a query filter to filter documents by id."""
        return include_ids

    def similarity_search_by_vector(
        self, query_embedding: list[float] | np.ndarray, k: int = 10, **kwargs: Any
    ) -> list[VectorStoreSearchResult]:
        """Perform a vector-based similarity search."""
        table_name = self.index_name
        self.cursor.execute(
            f"""
            SELECT id, text, attributes, vector <=> %s::vector as distance 
            FROM {table_name} 
            ORDER BY distance ASC 
            LIMIT %s
        """,
            (query_embedding, k),
        )

        results = []
        for id, text, attributes, distance in self.cursor.fetchall():
            results.append(
                VectorStoreSearchResult(
                    document=VectorStoreDocument(
                        id=id,
                        text=text,
                        vector=None,  # Optimization: don't return vector
                        attributes=attributes
                        if isinstance(attributes, dict)
                        else json.loads(attributes),
                    ),
                    score=1 - distance,
                )
            )
        return results

    def similarity_search_by_text(
        self, text: str, text_embedder: TextEmbedder, k: int = 10, **kwargs: Any
    ) -> list[VectorStoreSearchResult]:
        """Perform a similarity search using a given input text."""
        query_embedding = text_embedder(text)
        if query_embedding:
            return self.similarity_search_by_vector(query_embedding, k)
        return []

    def search_by_id(self, id: str) -> VectorStoreDocument:
        """Search for a document by id."""
        table_name = self.index_name
        self.cursor.execute(
            f"SELECT id, text, attributes FROM {table_name} WHERE id = %s", (id,)
        )
        row = self.cursor.fetchone()
        if row:
            return VectorStoreDocument(
                id=row[0],
                text=row[1],
                vector=None,
                attributes=row[2] if isinstance(row[2], dict) else json.loads(row[2]),
            )
        return VectorStoreDocument(id=id, text=None, vector=None)
