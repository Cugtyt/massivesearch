"""Search Engine Module."""

from supersearch.search_engine.base_engine import (
    BaseSearchEngine,
    BaseSearchEngineConfig,
)
from supersearch.search_engine.bool_engine import (
    BoolSearchEngine,
    BoolSearchEngineConfig,
)
from supersearch.search_engine.date_engine import (
    DateSearchEngine,
    DateSearchEngineConfig,
)
from supersearch.search_engine.hub import (
    SearchEngineRegisterError,
    registered_search_engines,
)
from supersearch.search_engine.number_engine import (
    NumberSearchEngine,
    NumberSearchEngineConfig,
)
from supersearch.search_engine.text_engine import (
    TextSearchEngine,
    TextSearchEngineConfig,
)
from supersearch.search_engine.vector_engine import (
    VectorSearchEngine,
    VectorSearchEngineConfig,
)

__all__ = [
    "BaseSearchEngine",
    "BaseSearchEngineConfig",
    "BoolSearchEngine",
    "BoolSearchEngineConfig",
    "DateSearchEngine",
    "DateSearchEngineConfig",
    "NumberSearchEngine",
    "NumberSearchEngineConfig",
    "SearchEngineRegisterError",
    "TextSearchEngine",
    "TextSearchEngineConfig",
    "VectorSearchEngine",
    "VectorSearchEngineConfig",
    "registered_search_engines",
]
