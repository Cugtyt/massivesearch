"""Date search engine."""

from supersearch.search_engine.base_engine import (
    BaseSearchEngine,
    BaseSearchEngineConfig,
)


class DateSearchEngineConfig(BaseSearchEngineConfig):
    """Config for date search engine."""

    format: str


class DateSearchEngine(BaseSearchEngine):
    """date search engine."""

    config: DateSearchEngineConfig | None
