"""Vector search engine."""

from pydantic import Field

from massivesearch.spec.base_search_engine import (
    BaseSearchEngine,
    BaseSearchEngineArguments,
    BaseSearchEngineConfig,
    BaseSearchResult,
)
from massivesearch.spec.builder import SpecBuilder

spec_builder = SpecBuilder()


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


@spec_builder.search_engine("vector_search")
class VectorSearchEngine(BaseSearchEngine):
    """Vector search engine."""

    config: VectorSearchEngineConfig

    def search(self, arguments: VectorSearchEngineArguments) -> BaseSearchResult:
        """Search for vector values."""
        msg = "Vector search engine is not implemented yet."
        raise NotImplementedError(msg)
