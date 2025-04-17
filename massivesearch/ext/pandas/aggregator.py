"""Aggregator for pandas DataFrames."""

import asyncio

import pandas as pd

from massivesearch.aggregator import BaseAggregator, MassiveSearchTasks
from massivesearch.ext.pandas.types import (
    PandasAggregatorResult,
)


class PandasAggregator(BaseAggregator):
    """Aggregator class."""

    file_path: str

    async def aggregate(
        self,
        tasks: MassiveSearchTasks,
    ) -> PandasAggregatorResult:
        """Aggregate the search results."""
        all_common_indices: list[pd.Index] = []

        for single_search_task in tasks:
            keys = list(single_search_task.keys())
            task_values = list(single_search_task.values())
            results = await asyncio.gather(*task_values)

            result_dict = dict(zip(keys, results, strict=False))

            partial_results = list(result_dict.values())
            if partial_results:
                common_indices = partial_results[0]
                for partial_result in partial_results[1:]:
                    common_indices = common_indices.intersection(partial_result)
                if len(common_indices) > 0:
                    all_common_indices.append(common_indices)

        book_df = pd.read_csv(self.file_path)
        if not all_common_indices:
            return pd.DataFrame()

        final_indices = pd.Index([])
        if all_common_indices:
            final_indices = all_common_indices[0]
            for idx in all_common_indices[1:]:
                final_indices = final_indices.union(idx)

        if not final_indices.empty:
            return book_df.loc[final_indices]
        return pd.DataFrame()
