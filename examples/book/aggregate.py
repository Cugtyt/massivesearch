"""Book aggregate."""  # noqa: INP001

import pandas as pd

from massivesearch.aggregator.aggregator import Aggregator
from massivesearch.worker.worker import WorkerExecuteResult


class BookAggregator(Aggregator):
    """Book aggregator."""

    def aggregate(
        self,
        search_results: list[dict[str, WorkerExecuteResult]],
    ) -> pd.DataFrame:
        """Aggregate the search results."""
        book_results = []
        for single_search_result in search_results:
            for search_result in single_search_result.result.values():
                book_results.append(search_result)
        books = pd.concat(book_results)
        return books[~books.index.duplicated(keep="first")]
