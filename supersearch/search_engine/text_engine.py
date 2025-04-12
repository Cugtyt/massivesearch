"""Text search engine."""

from typing import Literal

from pydantic import Field

from supersearch.search_engine.base_engine import (
    BaseSearchEngine,
    BaseSearchEngineConfig,
)
from supersearch.search_engine.hub import search_engine


class TextSearchEngineConfig(BaseSearchEngineConfig):
    """Config for text search engines."""

    matching_strategy: str = Literal["exact", "contains", "starts_with", "ends_with"]


class TextSearchEngineArguments(BaseSearchEngineConfig):
    """Arguments for text search engines."""

    keywords: list[str] = Field(
        description="List of keywords for the search engine.",
    )


@search_engine("text")
class TextSearchEngine(BaseSearchEngine):
    """Text search engine."""

    config: TextSearchEngineConfig | None
    arguments: TextSearchEngineArguments | None = None
