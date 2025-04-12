"""Number search engine."""

from pydantic import BaseModel

from search_engine.base_engine import BaseSearchEngineConfig


class NumberSearchEngineConfig(BaseSearchEngineConfig):
    """Default arguments for number search engines."""

class NumberSearchEngine(BaseModel):
    """Number search engine."""

    config: NumberSearchEngineConfig
