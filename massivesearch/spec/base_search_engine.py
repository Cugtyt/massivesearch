"""Base class for search engines."""

from abc import abstractmethod

from pydantic import BaseModel


class BaseSearchEngineConfig(BaseModel):
    """Config for search engines."""


class BaseSearchEngineArguments(BaseModel):
    """Arguments for search engines."""


class BaseSearchResult:
    """Base class for search results."""


class BaseSearchEngine(BaseModel):
    """Base class for search engines."""

    config: BaseSearchEngineConfig

    @abstractmethod
    def search(self, arguments: BaseSearchEngineArguments) -> BaseSearchResult:
        """Search for the given arguments."""
