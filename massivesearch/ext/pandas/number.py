"""Number search engine for Pandas."""

from typing import Self

import pandas as pd
from pydantic import BaseModel, Field, model_validator

from massivesearch.ext.pandas.types import (
    PandasBaseSearchEngineMixin,
)
from massivesearch.search_engine import (
    BaseSearchEngineArguments,
)
from massivesearch.search_engine.base import BaseSearchEngine


class NumberRange(BaseModel):
    """Number range."""

    start_number: float | None = Field(
        description="Start number for the search engine.The start number is inclusive.",
    )
    end_number: float | None = Field(
        description="End number for the search engine.The end number is inclusive.",
    )

    @model_validator(mode="after")
    def check_range(self) -> Self:
        """Validate the number range."""
        if self.start_number is None and self.end_number is None:
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


class PandasNumberSearchEngine(PandasBaseSearchEngineMixin, BaseSearchEngine):
    """Number search engine."""

    async def search(
        self,
        arguments: PandasNumberSearchEngineArguments,
    ) -> pd.Index:
        """Search for numbers."""
        data = self.load_df()

        if len(arguments.number_ranges) == 0:
            return data.index

        data_series = data[self.column_name]
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
            return data.index
        combined_mask = masks[0]
        for mask in masks[1:]:
            combined_mask |= mask
        return data.index[combined_mask]
