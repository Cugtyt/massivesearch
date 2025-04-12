"""Vector search engine."""

from pydantic import Field

from supersearch.search_engine.base_engine import (
    BaseSearchEngine,
    BaseSearchEngineConfig,
)
from supersearch.search_engine.hub import search_engine


class VectorSearchEngineConfig(BaseSearchEngineConfig):
    """Config for vector search engines."""


class VectorSearchEngineArguments(BaseSearchEngineConfig):
    """Arguments for vector search engines."""

    querys: list[str] = Field(
        description="List of querys for the search engine.",
    )


@search_engine("vector")
class VectorSearchEngine(BaseSearchEngine):
    """Vector search engine."""

    config: VectorSearchEngineConfig | None
    arguments: VectorSearchEngineArguments | None = None
