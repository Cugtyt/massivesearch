"""Text search engine for Pandas."""

from typing import Literal

from pydantic import Field

from massivesearch.ext.pandas.types import (
    PandasBaseSearchEngine,
    PandasSearchResultIndex,
)
from massivesearch.search_engine import BaseSearchEngineArguments


class PandasTextSearchEngineArguments(BaseSearchEngineArguments):
    """Arguments for text search engines."""

    keywords: list[str] = Field(
        description="List of keywords for the search engine.",
    )


class PandasTextSearchEngine(PandasBaseSearchEngine):
    """Text search engine."""

    matching_strategy: Literal["exact", "contains", "starts_with", "ends_with"]

    def search(
        self,
        arguments: PandasTextSearchEngineArguments,
    ) -> PandasSearchResultIndex:
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
                indices = data.index[data_series_lower.str.startswith(keywords_lower)]
            case "ends_with":
                indices = data.index[data_series_lower.str.endswith(keywords_lower)]
            case _:
                msg = "Invalid matching strategy."
                raise ValueError(msg)
        return indices
