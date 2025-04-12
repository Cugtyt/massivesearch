"""Text search engine."""

from search_engine.base_engine import BaseSearchEngine, BaseSearchEngineConfig


class TextSearchEngineConfig(BaseSearchEngineConfig):
    """Config for text search engines."""


class TextSearchEngine(BaseSearchEngine):
    """Text search engine."""

    config: TextSearchEngineConfig
