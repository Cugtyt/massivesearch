"""Vector search engine."""

from supersearch.search_engine.base_engine import (
    BaseSearchEngine,
    BaseSearchEngineConfig,
)


class VectorSearchEngineConfig(BaseSearchEngineConfig):
    """Config for vector search engines."""


class VectorSearchEngine(BaseSearchEngine):
    """Vector search engine."""

    config: VectorSearchEngineConfig | None
