"""Aggregator."""

from abc import ABC, abstractmethod

from pydantic import BaseModel

from massivesearch.worker import WorkerExecuteResult


class AggregatorResult:
    """Aggregator result."""


class AggregatorConfig(BaseModel):
    """Aggregator result config."""


class Aggregator(ABC):
    """Aggregator class."""

    config: AggregatorConfig

    def __init__(self, config: AggregatorConfig) -> None:
        """Initialize the aggregator."""
        self.config = config

    @abstractmethod
    def aggregate(self, worker_results: list[WorkerExecuteResult]) -> AggregatorResult:
        """Aggregate the search results."""
        msg = "Subclasses must implement this method."
        raise NotImplementedError(msg)
