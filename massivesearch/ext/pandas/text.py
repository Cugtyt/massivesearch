"""Text search engine for Pandas."""

from typing import Literal

import pandas as pd
from pydantic import BaseModel, Field

from massivesearch.ext.pandas.types import (
    PandasBaseSearchEngineMixin,
)
from massivesearch.search_engine.base import BaseSearchEngine


class PandasTextSearchEngineArguments(BaseModel):
    """Arguments for text search engines."""

    keywords: list[str] = Field(
        description="List of keywords for the search engine.",
    )


class PandasTextSearchEngine(PandasBaseSearchEngineMixin, BaseSearchEngine):
    """Text search engine."""

    matching_strategy: Literal["exact", "contains", "starts_with", "ends_with"]

    async def search(
        self,
        arguments: PandasTextSearchEngineArguments,
    ) -> pd.Index:
        """Search for text values."""
        data = self.load_df()
        data_series_lower = data[self.column_name].str.lower()
        keywords_lower = [keyword.lower() for keyword in arguments.keywords]
        match self.matching_strategy:
            case "exact":
                indices = data.index[data_series_lower.isin(keywords_lower)]
            case "contains":
                indices = data.index[
                    data_series_lower.str.contains("|".join(keywords_lower))
                ]
            case "starts_with":
                indices = data.index[
                    data_series_lower.str.startswith(tuple(keywords_lower))
                ]
            case "ends_with":
                indices = data.index[
                    data_series_lower.str.endswith(tuple(keywords_lower))
                ]
            case _:
                msg = "Invalid matching strategy."
                raise ValueError(msg)
        return indices
