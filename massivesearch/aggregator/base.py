"""Aggregator."""

from abc import abstractmethod
from asyncio import Task

from pydantic import BaseModel, ConfigDict

from massivesearch.search_engine.base import BaseSearchResultIndex

MassiveSearchTasks = list[dict[str, Task[BaseSearchResultIndex]]]


class BaseAggregatorResult:
    """Aggregator result."""


class BaseAggregator(BaseModel):
    """Aggregator class."""

    model_config = ConfigDict(extra="ignore")

    @abstractmethod
    async def aggregate(
        self,
        tasks: MassiveSearchTasks,
    ) -> BaseAggregatorResult:
        """Aggregate the search results."""
