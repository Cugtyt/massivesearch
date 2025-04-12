"""Number search engine."""

from supersearch.search_engine.base_engine import (
    BaseSearchEngine,
    BaseSearchEngineConfig,
)


class NumberSearchEngineConfig(BaseSearchEngineConfig):
    """Config for number search engine."""


class NumberSearchEngine(BaseSearchEngine):
    """Number search engine."""

    config: NumberSearchEngineConfig | None
