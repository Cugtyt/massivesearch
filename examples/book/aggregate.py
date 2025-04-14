"""Book aggregate."""  # noqa: INP001

import pandas as pd
from data_loader import load_data

from massivesearch.aggregator.aggregator import Aggregator
from massivesearch.worker.worker import WorkerExecuteResult


class BookAggregator(Aggregator):
    """Book aggregator."""

    def aggregate(
        self,
        execute_results: list[dict[str, WorkerExecuteResult]],
    ) -> pd.DataFrame:
        """Aggregate the search results."""
        all_common_indices = []

        for single_search_result in execute_results:
            partial_results = list(single_search_result.result.values())
            if partial_results and len(partial_results) > 0:
                common_indices = partial_results[0]
                for partial_result in partial_results[1:]:
                    common_indices = common_indices.intersection(partial_result)

                if len(common_indices) > 0:
                    all_common_indices.append(common_indices)

        book_df = load_data()
        if all_common_indices:
            combined_indices = pd.Index([]).union(*all_common_indices)
            unique_indices = combined_indices[
                ~combined_indices.duplicated(keep="first")
            ]
            return book_df.loc[unique_indices]

        return pd.DataFrame()
