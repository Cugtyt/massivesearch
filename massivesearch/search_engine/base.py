"""Base class for search engines."""

from abc import abstractmethod
from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict
from pydantic.generics import GenericModel


class BaseSearchEngineArguments(BaseModel):
    """Arguments for search engines."""


ArgT = TypeVar("ArgT", bound=BaseSearchEngineArguments)


class BaseSearchResultIndex:
    """Base class for search results."""


ResT = TypeVar("ResT", bound=BaseSearchResultIndex)


class BaseSearchEngine(GenericModel, Generic[ArgT, ResT]):
    """Base class for search engines."""

    model_config = ConfigDict(extra="ignore")

    @abstractmethod
    async def search(
        self,
        arguments: ArgT,
    ) -> ResT:
        """Search for the given arguments."""
