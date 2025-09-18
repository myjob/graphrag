# Copyright (c) 2024 Microsoft Corporation.
# Licensed under the MIT License

"""A module containing 'SummarizedDescriptionResult' model."""

from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Any, Literal, NamedTuple

from graphrag.cache.pipeline_cache import PipelineCache

StrategyConfig = dict[str, Any]


@dataclass
class SummarizedDescriptionResult:
    """Entity summarization result class definition."""

    id: str | tuple[str, str]
    description: str


SummarizationStrategy = Callable[
    [
        str | tuple[str, str],
        list[str],
        PipelineCache,
        StrategyConfig,
    ],
    Awaitable[SummarizedDescriptionResult],
]


class DescriptionSummarizeRow(NamedTuple):
    """DescriptionSummarizeRow class definition."""

    graph: Any


SummarizeStrategyType = Literal["graph_intelligence"]
"""SummarizeStrategyType class definition."""
