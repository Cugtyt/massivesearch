"""Base class for search engines."""

from abc import abstractmethod
from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict
from pydantic.generics import GenericModel


class BaseSearchEngineArguments(BaseModel):
    """Arguments for search engines."""


SearchArgT = TypeVar("SearchArgT", bound=BaseSearchEngineArguments)


SearchResT = TypeVar("SearchResT")


class BaseSearchEngine(GenericModel, Generic[SearchArgT, SearchResT]):
    """Base class for search engines."""

    model_config = ConfigDict(extra="ignore")

    @abstractmethod
    async def search(
        self,
        arguments: SearchArgT,
    ) -> SearchResT:
        """Search for the given arguments."""
