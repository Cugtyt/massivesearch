"""Base class for search engines."""

from abc import abstractmethod
from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict

SearchArgT = TypeVar("SearchArgT", bound=BaseModel)


SearchResT = TypeVar("SearchResT")


class BaseSearchEngine(BaseModel, Generic[SearchArgT, SearchResT]):
    """Base class for search engines."""

    model_config = ConfigDict(extra="ignore")

    @abstractmethod
    async def search(
        self,
        arguments: SearchArgT,
    ) -> SearchResT:
        """Search for the given arguments."""
