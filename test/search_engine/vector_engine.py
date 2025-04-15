"""Vector search engine."""

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


class VectorSearchEngineArguments(BaseSearchEngineArguments):
    """Arguments for vector search engines."""

    querys: list[str] = Field(
        description="List of language querys to to query the vector search engine.",
    )


@spec_builder.search_engine("vector_search")
class VectorSearchEngine(BaseSearchEngine):
    """Vector search engine."""

    top_k: int = Field(
        default=5,
        description="Number of top results to return from the vector search engine.",
    )
    distance_metric: str = Field(
        default="cosine",
        description="Distance metric to use for vector search.",
    )

    def search(self, arguments: VectorSearchEngineArguments) -> BaseSearchResultIndex:
        """Search for vector values."""
        msg = "Vector search engine is not implemented yet."
        raise NotImplementedError(msg)
