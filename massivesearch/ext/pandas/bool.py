"""Boolean search engine for Pandas."""

from typing import Self

from pydantic import Field, model_validator

from massivesearch.ext.pandas.types import (
    PandasBaseSearchEngine,
    PandasSearchResultIndex,
)
from massivesearch.search_engine import (
    BaseSearchEngineArguments,
)


class PandasBoolSearchEngineArguments(BaseSearchEngineArguments):
    """Arguments for boolean search engines.

    If both `select_true` and `select_false` are set to true,
    the search engine will return all results.
    If both are set to false, it will raise error.
    If one is set to true, it will return only the corresponding results.
    """

    select_true: bool = Field(
        description="Select true values",
    )
    select_false: bool = Field(
        description="Select false values",
    )

    @model_validator(mode="after")
    def validate(self) -> Self:
        """Validate the arguments."""
        if not self.select_true and not self.select_false:
            msg = "Both select_true and select_false cannot be false."
            raise ValueError(msg)
        return self


class BoolSearchEngine(PandasBaseSearchEngine):
    """Boolean search engine."""

    async def search(
        self,
        arguments: PandasBoolSearchEngineArguments,
    ) -> PandasSearchResultIndex:
        """Search for boolean values."""
        data = self.load_df()
        data_series = data[self.config.column_name]
        if arguments.select_true and arguments.select_false:
            return data.index
        if arguments.select_true:
            return data.index[data_series]
        if arguments.select_false:
            return data.index[~data_series]
        return data.index
