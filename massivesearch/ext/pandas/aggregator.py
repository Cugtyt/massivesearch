"""Aggregator for pandas DataFrames."""

import pandas as pd

from massivesearch.aggregator import BaseAggregator
from massivesearch.ext.pandas.types import (
    PandasAggregatorResult,
)
from massivesearch.pipe import SearchResult


class PandasAggregator(BaseAggregator):
    """Aggregator class."""

    file_path: str

    def aggregate(
        self,
        worker_results: SearchResult,
    ) -> PandasAggregatorResult:
        """Aggregate the search results."""
        all_common_indices: list[pd.Index] = []

        for single_search_result in worker_results:
            partial_results = list(single_search_result.values())
            if partial_results and len(partial_results) > 0:
                common_indices = partial_results[0]
                for partial_result in partial_results[1:]:
                    common_indices = common_indices.intersection(partial_result)

                if len(common_indices) > 0:
                    all_common_indices.append(common_indices)

        book_df = pd.read_csv(self.file_path)
        if not all_common_indices:
            return pd.DataFrame()

        # Start with an empty index or the first index
        final_indices = pd.Index([])
        if all_common_indices:
            final_indices = all_common_indices[0]
            # Compute the union with the rest of the indices
            for idx in all_common_indices[1:]:
                final_indices = final_indices.union(idx)

        if not final_indices.empty:
            return book_df.loc[final_indices]
        return pd.DataFrame()
