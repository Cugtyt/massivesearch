"""Aggregator for pandas DataFrames."""

from abc import ABC, abstractmethod

import pandas as pd

from massivesearch.ext.pandas.types import PandasAggregatorResult
from massivesearch.worker import WorkerExecuteResult


class PandasAggregator(ABC):
    """Aggregator class."""

    @abstractmethod
    def load_df(self) -> pd.DataFrame:
        """Load data for aggregation."""

    def aggregate(
        self,
        worker_results: list[WorkerExecuteResult],
    ) -> PandasAggregatorResult:
        """Aggregate the search results."""
        all_common_indices = []

        for single_search_result in worker_results:
            partial_results = list(single_search_result.result.values())
            if partial_results and len(partial_results) > 0:
                common_indices = partial_results[0]
                for partial_result in partial_results[1:]:
                    common_indices = common_indices.intersection(partial_result)

                if len(common_indices) > 0:
                    all_common_indices.append(common_indices)

        book_df = self.load_df()
        if all_common_indices:
            combined_indices = pd.Index([]).union(*all_common_indices)
            unique_indices = combined_indices[
                ~combined_indices.duplicated(keep="first")
            ]
            return book_df.loc[unique_indices]

        return pd.DataFrame()
