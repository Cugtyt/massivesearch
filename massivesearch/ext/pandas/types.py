"""Types for pandas search engine."""

from abc import ABC

import pandas as pd

from massivesearch.aggregator import AggregatorConfig
from massivesearch.search_engine.base import (
    BaseSearchEngine,
    BaseSearchEngineConfig,
    BaseSearchResultIndex,
)


class PandasSearchResultIndex(pd.Index, BaseSearchResultIndex):
    """Result of pandas search engine."""


class PandasBaseSearchEngineConfig(BaseSearchEngineConfig):
    """Config for pandas search engine."""

    file_path: str
    column_name: str


class PandasBaseSearchEngine(BaseSearchEngine, ABC):
    """Pandas base search engine."""

    config: PandasBaseSearchEngineConfig

    def load_df(self) -> pd.DataFrame:
        """Load data for the search engine."""
        return pd.read_csv(self.config.file_path)


class PandasAggregatorResult(pd.DataFrame):
    """Aggregator result for pandas DataFrames."""


class PandasAggregatorConfig(AggregatorConfig):
    """Config for pandas aggregator."""

    file_path: str
