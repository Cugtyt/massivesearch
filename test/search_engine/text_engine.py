"""Text search engine."""

from typing import Literal

from pydantic import Field

from massivesearch.search_engine.base import (
    BaseSearchEngine,
    BaseSearchEngineArguments,
    BaseSearchResultIndex,
)
from massivesearch.spec import (
    SpecBuilder,
)

spec_builder = SpecBuilder()


class TextSearchEngineArguments(BaseSearchEngineArguments):
    """Arguments for text search engines."""

    keywords: list[str] = Field(
        description="List of keywords for the search engine.",
    )


@spec_builder.search_engine("text_search")
class TextSearchEngine(BaseSearchEngine):
    """Text search engine."""

    matching_strategy: Literal["exact", "contains", "starts_with", "ends_with"]

    def search(self, arguments: TextSearchEngineArguments) -> BaseSearchResultIndex:
        """Search for text values."""
        msg = "Text search engine is not implemented yet."
        raise NotImplementedError(msg)
