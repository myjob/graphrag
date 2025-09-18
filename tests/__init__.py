# Copyright (c) 2024 Microsoft Corporation.
# Licensed under the MIT License


"""Tests for the GraphRAG LLM module."""

# Register MOCK providers
from graphrag.language_model.factory import ModelFactory
from tests.mock_provider import MockChatLLM, MockEmbeddingLLM

ModelFactory.register_chat("mock_chat", lambda **kwargs: MockChatLLM(**kwargs))
ModelFactory.register_embedding(
    "mock_embedding", lambda **kwargs: MockEmbeddingLLM(**kwargs)
)
