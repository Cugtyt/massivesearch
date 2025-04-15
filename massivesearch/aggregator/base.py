"""Aggregator."""

from abc import abstractmethod

from pydantic import BaseModel

from massivesearch.search_engine.base import BaseSearchResultIndex

WorkerSearchResult = list[dict[str, BaseSearchResultIndex]]


class AggregatorResult:
    """Aggregator result."""


class AggregatorConfig(BaseModel):
    """Aggregator result config."""


class Aggregator(BaseModel):
    """Aggregator class."""

    config: AggregatorConfig

    @abstractmethod
    def aggregate(self, worker_results: WorkerSearchResult) -> AggregatorResult:
        """Aggregate the search results."""
        msg = "Subclasses must implement this method."
        raise NotImplementedError(msg)
