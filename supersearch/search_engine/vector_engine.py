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

    top_k: int = Field(
        default=5,
        description="Number of top results to return from the vector search engine.",
    )
    distance_metric: str = Field(
        default="cosine",
        description="Distance metric to use for vector search.",
    )


class VectorSearchEngineArguments(BaseSearchEngineArguments):
    """Arguments for vector search engines."""

    querys: list[str] = Field(
        description="List of language querys to to query the vector search engine.",
    )


class VectorSearchResult(BaseSearchResult):
    """Result of vector search."""


@search_engine("vector_search")
class VectorSearchEngine(BaseSearchEngine):
    """Vector search engine."""

    config: VectorSearchEngineConfig

    def search(self, arguments: VectorSearchEngineArguments) -> VectorSearchResult:
        """Search for vector values."""
        if not isinstance(arguments, VectorSearchEngineArguments):
            msg = "Invalid arguments type. Expected VectorSearchEngineArguments."
            raise TypeError(msg)

        return VectorSearchResult()
