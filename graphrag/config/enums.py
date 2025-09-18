# Copyright (c) 2024 Microsoft Corporation.
# Licensed under the MIT License

"""A module containing config enums."""

from __future__ import annotations

from enum import Enum
from typing import Literal

CacheType = Literal["file", "memory", "none", "blob", "cosmosdb"]
"""The cache configuration type for the pipeline."""


InputFileType = Literal["csv", "text", "json"]
"""The input file type for the pipeline."""

StorageType = Literal["file", "blob", "memory", "cosmosdb"]
"""The output type for the pipeline."""

VectorStoreType = Literal["lancedb", "azure_ai_search", "cosmosdb"]
"""The supported vector store types."""

ReportingType = Literal["file", "blob"]
"""The reporting configuration type for the pipeline."""

ModelType = Literal[
    "openai_embedding",
    "azure_openai_embedding",
    "openai_chat",
    "azure_openai_chat",
    "mock_chat",
    "mock_embedding",
]
"""LLMType enum class definition."""

AuthType = Literal["api_key", "azure_managed_identity"]
"""AuthType enum class definition."""

AsyncType = Literal["asyncio", "threaded"]
"""Enum for the type of async to use."""

ChunkStrategyType = Literal["tokens", "sentence"]
"""ChunkStrategy class definition."""

NounPhraseExtractorType = Literal["regex_english", "syntactic_parser", "cfg"]
"""Noun phrase extractor based on dependency parsing and NER using SpaCy."""

ModularityMetric = Literal["graph", "lcc", "weighted_components"]
"""Enum for the modularity metric to use."""


class SearchMethod(Enum):
    """The type of search to run."""

    LOCAL = "local"
    GLOBAL = "global"
    DRIFT = "drift"
    BASIC = "basic"

    def __str__(self):
        """Return the string representation of the enum value."""
        return self.value


class IndexingMethod(str, Enum):
    """Enum for the type of indexing to perform."""

    Standard = "standard"
    """Traditional GraphRAG indexing, with all graph construction and summarization performed by a language model."""
    Fast = "fast"
    """Fast indexing, using NLP for graph construction and language model for summarization."""
    StandardUpdate = "standard-update"
    """Incremental update with standard indexing."""
    FastUpdate = "fast-update"
    """Incremental update with fast indexing."""
