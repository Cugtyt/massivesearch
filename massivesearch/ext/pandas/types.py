"""Types for pandas search engine."""

from abc import ABC

import pandas as pd

from massivesearch.search_engine.base import (
    BaseSearchEngine,
    BaseSearchResultIndex,
)


class PandasSearchResultIndex(pd.Index, BaseSearchResultIndex):
    """Result of pandas search engine."""


class PandasBaseSearchEngine(BaseSearchEngine, ABC):
    """Pandas base search engine."""

    file_path: str
    column_name: str

    def load_df(self) -> pd.DataFrame:
        """Load data for the search engine."""
        return pd.read_csv(self.file_path)


class PandasAggregatorResult(pd.DataFrame):
    """Aggregator result for pandas DataFrames."""
