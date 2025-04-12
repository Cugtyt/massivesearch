"""Text search engine."""

from pydantic import BaseModel

from search_engine.base_engine import BaseSearchEngineConfig


class TextSearchEngineConfig(BaseSearchEngineConfig):
    """Default arguments for text search engines."""


class TextSearchEngine(BaseModel):
    """Text search engine."""

    default_arguments: TextSearchEngineConfig
