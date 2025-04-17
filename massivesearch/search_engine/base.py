"""Base class for search engines."""

from abc import abstractmethod

from pydantic import BaseModel, ConfigDict


class BaseSearchEngineArguments(BaseModel):
    """Arguments for search engines."""


class BaseSearchResultIndex:
    """Base class for search results."""


class BaseSearchEngine(BaseModel):
    """Base class for search engines."""

    model_config = ConfigDict(extra="ignore")

    @abstractmethod
    async def search(
        self,
        arguments: BaseSearchEngineArguments,
    ) -> BaseSearchResultIndex:
        """Search for the given arguments."""
