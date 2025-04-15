"""Number search engine for Pandas."""

from typing import Self

import pandas as pd
from pydantic import BaseModel, Field, model_validator

from massivesearch.ext.pandas.types import (
    PandasBaseSearchEngine,
    PandasSearchResultIndex,
)
from massivesearch.search_engine import (
    BaseSearchEngineArguments,
)


class NumberRange(BaseModel):
    """Number range."""

    start_number: float | None = Field(
        description="Start number for the search engine.The start number is inclusive.",
    )
    end_number: float | None = Field(
        description="End number for the search engine.The end number is inclusive.",
    )

    @model_validator(mode="after")
    def validate(self) -> Self:
        """Validate the arguments."""
        if not self.start_number and not self.end_number:
            msg = "Both start_number and end_number cannot be None."
            raise ValueError(msg)
        if (
            self.start_number is not None
            and self.end_number is not None
            and self.start_number > self.end_number
        ):
            msg = "start_number must be less than or equal to end_number."
            raise ValueError(msg)
        return self


class PandasNumberSearchEngineArguments(BaseSearchEngineArguments):
    """Arguments for number search engine."""

    number_ranges: list[NumberRange] = Field(
        description="List of number ranges for the search engine.",
    )


class PandasNumberSearchEngine(PandasBaseSearchEngine):
    """Number search engine."""

    def search(
        self,
        arguments: PandasNumberSearchEngineArguments,
    ) -> PandasSearchResultIndex:
        """Search for numbers."""
        data = self.load_df()

        if len(arguments.number_ranges) == 0:
            return data.index

        data_series = data[self.config.column_name]
        masks = []

        for number_range in arguments.number_ranges:
            start_number = number_range.start_number
            end_number = number_range.end_number
            if start_number is not None and end_number is not None:
                current_mask = (data_series >= start_number) & (
                    data_series <= end_number
                )
            elif start_number is not None:
                current_mask = data_series >= start_number
            elif end_number is not None:
                current_mask = data_series <= end_number
            else:
                continue
            masks.append(current_mask)

        if not masks:
            return pd.Index([])
        combined_mask = masks[0]
        for mask in masks[1:]:
            combined_mask |= mask
        return data.index[combined_mask]
