"""Text search engine."""

from typing import Literal

from pydantic import Field

from supersearch.spec.base_search_engine import (
    BaseSearchEngine,
    BaseSearchEngineArguments,
    BaseSearchEngineConfig,
    BaseSearchResult,
)
from supersearch.spec.builder import SpecBuilder

spec_builder = SpecBuilder()


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


@spec_builder.search_engine("text_search")
class TextSearchEngine(BaseSearchEngine):
    """Text search engine."""

    config: TextSearchEngineConfig

    def search(self, arguments: TextSearchEngineArguments) -> TextSearchResult:
        """Search for text values."""
        if not isinstance(arguments, TextSearchEngineArguments):
            msg = "Invalid arguments type. Expected TextSearchEngineArguments."
            raise TypeError(msg)

        return TextSearchResult()
