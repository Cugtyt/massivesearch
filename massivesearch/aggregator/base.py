"""Aggregator."""

from abc import abstractmethod

from pydantic import BaseModel, ConfigDict

from massivesearch.search_engine.base import BaseSearchResultIndex

WorkerSearchResult = list[dict[str, BaseSearchResultIndex]]


class BaseAggregatorResult:
    """Aggregator result."""


class BaseAggregator(BaseModel):
    """Aggregator class."""

    model_config = ConfigDict(extra="ignore")

    @abstractmethod
    def aggregate(self, worker_results: WorkerSearchResult) -> BaseAggregatorResult:
        """Aggregate the search results."""
        msg = "Subclasses must implement this method."
        raise NotImplementedError(msg)
