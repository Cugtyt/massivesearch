"""Aggregator for pandas DataFrames."""

import asyncio

import pandas as pd

from massivesearch.aggregator import BaseAggregator, MassiveSearchTasks
from massivesearch.ext.pandas.types import (
    PandasAggregatorResult,
    PandasSearchResultIndex,
)


class PandasAggregator(BaseAggregator):
    """Aggregator class."""

    file_path: str

    async def aggregate(
        self,
        tasks: MassiveSearchTasks,
    ) -> PandasAggregatorResult:
        """Aggregate the search results."""
        all_common_indices = await self._process_search_tasks(tasks)

        book_df = pd.read_csv(self.file_path)
        if not all_common_indices:
            return PandasAggregatorResult()

        final_indices = self._merge_indices(all_common_indices)

        if not final_indices.empty:
            return PandasAggregatorResult(book_df.loc[final_indices])
        return PandasAggregatorResult()

    async def _process_search_tasks(
        self,
        tasks: MassiveSearchTasks,
    ) -> list[pd.Index]:
        """Process search tasks and return common indices for each task."""
        all_common_indices: list[pd.Index] = []

        for single_search_task in tasks:
            keys = list(single_search_task.keys())
            task_values = list(single_search_task.values())
            results = await asyncio.gather(*task_values)

            result_dict = dict(zip(keys, results, strict=False))
            common_indices = self._find_common_indices(list(result_dict.values()))

            if len(common_indices) > 0:
                all_common_indices.append(common_indices)

        return all_common_indices

    def _find_common_indices(self, partial_results: list) -> pd.Index:
        """Find common indices by intersecting all partial results."""
        if not partial_results:
            return pd.Index([])

        common_indices = partial_results[0]
        self._validate_result_type(common_indices)

        for partial_result in partial_results[1:]:
            self._validate_result_type(partial_result)
            common_indices = common_indices.intersection(partial_result)

        return common_indices

    def _validate_result_type(self, result: PandasSearchResultIndex) -> None:
        """Validate that a result is of type PandasSearchResultIndex."""
        if not isinstance(result, PandasSearchResultIndex):
            msg = f"Expected PandasSearchResultIndex, got {type(result)}"
            raise TypeError(msg)

    def _merge_indices(self, indices_list: list[pd.Index]) -> pd.Index:
        """Merge multiple indices using union operation."""
        if not indices_list:
            return pd.Index([])

        final_indices = indices_list[0]
        for idx in indices_list[1:]:
            final_indices = final_indices.union(idx)

        return final_indices
