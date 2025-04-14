"""Aggregator."""

from abc import ABC, abstractmethod

from massivesearch.worker import WorkerExecuteResult


class AggregatorResult:
    """Aggregator result."""


class Aggregator(ABC):
    """Aggregator class."""

    @abstractmethod
    def aggregate(self, worker_results: list[WorkerExecuteResult]) -> AggregatorResult:
        """Aggregate the search results."""
        msg = "Subclasses must implement this method."
        raise NotImplementedError(msg)
