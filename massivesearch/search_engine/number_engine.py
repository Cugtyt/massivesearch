"""Number search engine."""

from typing import Self

from pydantic import BaseModel, Field, model_validator

from massivesearch.spec.base_search_engine import (
    BaseSearchEngine,
    BaseSearchEngineArguments,
    BaseSearchEngineConfig,
    BaseSearchResultIndex,
)
from massivesearch.spec.builder import SpecBuilder

spec_builder = SpecBuilder()


class NumberSearchEngineConfig(BaseSearchEngineConfig):
    """Config for number search engine."""


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


class NumberSearchEngineArguments(BaseSearchEngineArguments):
    """Arguments for number search engine."""

    number_ranges: list[NumberRange] = Field(
        description="List of number ranges for the search engine.",
    )


@spec_builder.search_engine("number_search")
class NumberSearchEngine(BaseSearchEngine):
    """Number search engine."""

    config: NumberSearchEngineConfig

    def search(self, arguments: NumberSearchEngineArguments) -> BaseSearchResultIndex:
        """Search for numbers."""
        msg = "Number search engine is not implemented yet."
        raise NotImplementedError(msg)
