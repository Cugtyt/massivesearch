"""Types for pandas search engine."""

from abc import ABC, abstractmethod

import pandas as pd

from massivesearch.search_engine.base import (
    BaseSearchEngine,
    BaseSearchEngineConfig,
    BaseSearchResultIndex,
)


class PandasSearchResultIndex(pd.Index, BaseSearchResultIndex):
    """Result of pandas search engine."""


class PandasBaseSearchEngineConfig(BaseSearchEngineConfig):
    """Config for pandas search engine."""

    column_name: str


class PandasBaseSearchEngine(BaseSearchEngine, ABC):
    """Pandas base search engine."""

    config: PandasBaseSearchEngineConfig

    @abstractmethod
    def load_df(self) -> pd.DataFrame:
        """Load data for the search engine."""


class PandasAggregatorResult(pd.DataFrame):
    """Aggregator result for pandas DataFrames."""
