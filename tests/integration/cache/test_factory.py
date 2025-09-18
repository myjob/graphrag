# Copyright (c) 2024 Microsoft Corporation.
# Licensed under the MIT License
"""CacheFactory Tests.

These tests will test the CacheFactory class and the creation of each cache type that is natively supported.
"""

import sys

import pytest

from graphrag.cache.factory import CacheFactory
from graphrag.cache.json_pipeline_cache import JsonPipelineCache
from graphrag.cache.memory_pipeline_cache import InMemoryCache
from graphrag.cache.noop_pipeline_cache import NoopPipelineCache
from graphrag.cache.pipeline_cache import PipelineCache

# cspell:disable-next-line well-known-key
WELL_KNOWN_BLOB_STORAGE_KEY = "DefaultEndpointsProtocol=http;AccountName=devstoreaccount1;AccountKey=Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==;BlobEndpoint=http://127.0.0.1:10000/devstoreaccount1;"
# cspell:disable-next-line well-known-key
WELL_KNOWN_COSMOS_CONNECTION_STRING = "AccountEndpoint=https://127.0.0.1:8081/;AccountKey=C2y6yDjf5/R+ob0N8A7Cgv30VRDJIWEHLM+4QDU5DE2nQ9nDuVTqobD4b8mGGyPMbIZnqyMsEcaGQy67XIw/Jw=="


def test_create_noop_cache():
    kwargs = {}
    cache = CacheFactory.create_cache("none", kwargs)
    assert isinstance(cache, NoopPipelineCache)


def test_create_memory_cache():
    kwargs = {}
    cache = CacheFactory.create_cache("memory", kwargs)
    assert isinstance(cache, InMemoryCache)


def test_create_file_cache():
    kwargs = {"root_dir": "/tmp", "base_dir": "testcache"}
    cache = CacheFactory.create_cache("file", kwargs)
    assert isinstance(cache, JsonPipelineCache)


def test_create_blob_cache():
    kwargs = {
        "connection_string": WELL_KNOWN_BLOB_STORAGE_KEY,
        "container_name": "testcontainer",
        "base_dir": "testcache",
    }
    cache = CacheFactory.create_cache("blob", kwargs)
    assert isinstance(cache, JsonPipelineCache)


@pytest.mark.skipif(
    not sys.platform.startswith("win"),
    reason="cosmosdb emulator is only available on windows runners at this time",
)
def test_create_cosmosdb_cache():
    kwargs = {
        "connection_string": WELL_KNOWN_COSMOS_CONNECTION_STRING,
        "base_dir": "testdatabase",
        "container_name": "testcontainer",
    }
    cache = CacheFactory.create_cache("cosmosdb", kwargs)
    assert isinstance(cache, JsonPipelineCache)


def test_register_and_create_custom_cache():
    """Test registering and creating a custom cache type."""
    from unittest.mock import MagicMock

    # Create a mock that satisfies the PipelineCache interface
    custom_cache_class = MagicMock(spec=PipelineCache)
    # Make the mock return a mock instance when instantiated
    instance = MagicMock()
    instance.initialized = True
    custom_cache_class.return_value = instance

    CacheFactory.register("custom", lambda **kwargs: custom_cache_class(**kwargs))
    cache = CacheFactory.create_cache("custom", {})

    assert custom_cache_class.called
    assert cache is instance
    # Access the attribute we set on our mock
    assert cache.initialized is True  # type: ignore # Attribute only exists on our mock

    # Check if it's in the list of registered cache types
    assert "custom" in CacheFactory.get_cache_types()
    assert CacheFactory.is_supported_type("custom")


def test_get_cache_types():
    cache_types = CacheFactory.get_cache_types()
    # Check that built-in types are registered
    assert "none" in cache_types
    assert "memory" in cache_types
    assert "file" in cache_types
    assert "blob" in cache_types
    assert "cosmosdb" in cache_types


def test_create_unknown_cache():
    with pytest.raises(ValueError, match="Unknown cache type: unknown"):
        CacheFactory.create_cache("unknown", {})


def test_is_supported_type():
    # Test built-in types
    assert CacheFactory.is_supported_type("none")
    assert CacheFactory.is_supported_type("memory")
    assert CacheFactory.is_supported_type("file")
    assert CacheFactory.is_supported_type("blob")
    assert CacheFactory.is_supported_type("cosmosdb")

    # Test unknown type
    assert not CacheFactory.is_supported_type("unknown")


def test_register_class_directly_works():
    """Test that registering a class directly works (CacheFactory allows this)."""
    from graphrag.cache.pipeline_cache import PipelineCache

    class CustomCache(PipelineCache):
        def __init__(self, **kwargs):
            pass

        async def get(self, key: str):
            return None

        async def set(self, key: str, value, debug_data=None):
            pass

        async def has(self, key: str):
            return False

        async def delete(self, key: str):
            pass

        async def clear(self):
            pass

        def child(self, name: str):
            return self

    # CacheFactory allows registering classes directly (no TypeError)
    CacheFactory.register("custom_class", CustomCache)

    # Verify it was registered
    assert "custom_class" in CacheFactory.get_cache_types()
    assert CacheFactory.is_supported_type("custom_class")

    # Test creating an instance
    cache = CacheFactory.create_cache("custom_class", {})
    assert isinstance(cache, CustomCache)
