"""Boolean search engine."""

from supersearch.search_engine.base_engine import (
    BaseSearchEngine,
    BaseSearchEngineConfig,
)
from supersearch.search_engine.hub import search_engine


class BoolSearchEngineConfig(BaseSearchEngineConfig):
    """Config for boolean search engines."""


@search_engine("boolean")
class BoolSearchEngine(BaseSearchEngine):
    """Boolean search engine."""

    config: BoolSearchEngineConfig | None
