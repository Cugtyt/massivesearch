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

    matching_strategy: Literal["exact", "contains", "starts_with", "ends_with"]


class TextSearchEngineArguments(BaseSearchEngineArguments):
    """Arguments for text search engines."""

    keywords: list[str] = Field(
        description="List of keywords for the search engine.",
    )


@spec_builder.search_engine("text_search")
class TextSearchEngine(BaseSearchEngine):
    """Text search engine."""

    config: TextSearchEngineConfig

    def search(self, arguments: TextSearchEngineArguments) -> BaseSearchResult:
        """Search for text values."""
        msg = "Text search engine is not implemented yet."
        raise NotImplementedError(msg)
