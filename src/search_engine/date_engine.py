"""Date search engine."""

from search_engine.base_engine import BaseSearchEngine, BaseSearchEngineConfig


class DateSearchEngineConfig(BaseSearchEngineConfig):
    """Config for date search engine."""


class DateSearchEngine(BaseSearchEngine):
    """Text search engine."""

    config: DateSearchEngineConfig
