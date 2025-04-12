"""Base class for search engines."""

from pydantic import BaseModel


class BaseSearchEngineConfig(BaseModel):
    """Config for search engines."""

class BaseSearchEngine(BaseModel):
    """Base class for search engines."""

    config: BaseSearchEngineConfig | None = None
