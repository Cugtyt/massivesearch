"""Aggregator."""

from abc import abstractmethod
from asyncio import Task
from typing import Generic

from pydantic import ConfigDict
from pydantic.generics import GenericModel

from massivesearch.search_engine.base import SearchResT

type MassiveSearchTasks[T] = list[dict[str, Task[T]]]


class BaseAggregatorResult:
    """Aggregator result."""


class BaseAggregator(GenericModel, Generic[SearchResT]):
    """Aggregator class."""

    model_config = ConfigDict(extra="ignore")

    @abstractmethod
    async def aggregate(
        self,
        tasks: MassiveSearchTasks[SearchResT],
    ) -> BaseAggregatorResult:
        """Aggregate the search results."""
