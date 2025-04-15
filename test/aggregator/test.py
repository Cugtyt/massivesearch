"""Test Aggregator."""

from massivesearch.aggregator.base import BaseAggregator
from massivesearch.search_engine.base import BaseSearchResultIndex

WorkerSearchResult = list[dict[str, BaseSearchResultIndex]]


class TestAggregator(BaseAggregator):
    """Aggregator class."""

    def aggregate(self, worker_results: WorkerSearchResult) -> bool:
        """Aggregate the search results."""
        _ = worker_results
        return True
