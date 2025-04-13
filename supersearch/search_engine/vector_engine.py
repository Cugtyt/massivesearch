"""Vector search engine."""

from pydantic import Field

from supersearch.search_engine.base_engine import (
    BaseSearchEngine,
    BaseSearchEngineArguments,
    BaseSearchEngineConfig,
    BaseSearchResult,
)
from supersearch.search_engine.hub import search_engine


class VectorSearchEngineConfig(BaseSearchEngineConfig):
    """Config for vector search engines."""


class VectorSearchEngineArguments(BaseSearchEngineArguments):
    """Arguments for vector search engines."""

    querys: list[str] = Field(
        description="List of querys for the search engine.",
    )


class VectorSearchResult(BaseSearchResult):
    """Result of vector search."""


@search_engine("vector")
class VectorSearchEngine(BaseSearchEngine):
    """Vector search engine."""

    config: VectorSearchEngineConfig

    def search(self, arguments: VectorSearchEngineArguments) -> VectorSearchResult:
        """Search for vector values."""
        if not isinstance(arguments, VectorSearchEngineArguments):
            msg = "Invalid arguments type. Expected VectorSearchEngineArguments."
            raise TypeError(msg)

        return VectorSearchResult()
