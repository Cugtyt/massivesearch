"""Types for pandas search engine."""

from typing import Any

import pandas as pd
from pydantic import BaseModel

from massivesearch.aggregator.base import BaseAggregatorResult
from massivesearch.search_engine.base import (
    BaseSearchResultIndex,
)


class PandasSearchResultIndex(pd.Index[Any], BaseSearchResultIndex):
    """Result of pandas search engine."""


class PandasBaseSearchEngineMixin(BaseModel):
    """Pandas base search engine."""

    file_path: str
    column_name: str

    def load_df(self) -> pd.DataFrame:
        """Load data for the search engine."""
        return pd.read_csv(self.file_path)


class PandasAggregatorResult(BaseAggregatorResult, pd.DataFrame):
    """Aggregator result for pandas DataFrames."""
