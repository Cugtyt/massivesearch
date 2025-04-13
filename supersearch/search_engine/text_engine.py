"""Text search engine."""

from typing import Literal

from pydantic import Field

from supersearch.search_engine.base_engine import (
    BaseSearchEngine,
    BaseSearchEngineArguments,
    BaseSearchEngineConfig,
    BaseSearchResult,
)
from supersearch.search_engine.hub import search_engine


class TextSearchEngineConfig(BaseSearchEngineConfig):
    """Config for text search engines."""

    matching_strategy: str = Literal["exact", "contains", "starts_with", "ends_with"]


class TextSearchEngineArguments(BaseSearchEngineArguments):
    """Arguments for text search engines."""

    keywords: list[str] = Field(
        description="List of keywords for the search engine.",
    )


class TextSearchResult(BaseSearchResult):
    """Result of text search."""


@search_engine("text")
class TextSearchEngine(BaseSearchEngine):
    """Text search engine."""

    config: TextSearchEngineConfig

    def search(self, arguments: TextSearchEngineArguments) -> TextSearchResult:
        """Search for text values."""
        if not isinstance(arguments, TextSearchEngineArguments):
            msg = "Invalid arguments type. Expected TextSearchEngineArguments."
            raise TypeError(msg)

        return TextSearchResult()
