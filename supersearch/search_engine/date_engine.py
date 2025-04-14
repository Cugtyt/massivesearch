"""Date search engine."""

from datetime import UTC, datetime
from typing import Self

from pydantic import BaseModel, Field, model_validator

from supersearch.spec import (
    BaseSearchEngine,
    BaseSearchEngineArguments,
    BaseSearchEngineConfig,
    BaseSearchResult,
    SpecBuilder,
)

spec_builder = SpecBuilder()


class DateSearchEngineConfig(BaseSearchEngineConfig):
    """Config for date search engine."""

    format: str = "%Y-%m-%d"


class DateRange(BaseModel):
    """Date range."""

    start_date: str | None = Field(
        description="Start date for the search engine."
        "Format: YYYY-MM-DD, the start date is inclusive.",
    )
    end_date: str | None = Field(
        description="End date for the search engine."
        "Format: YYYY-MM-DD, the end date is inclusive.",
    )

    @model_validator(mode="after")
    def validate(self) -> Self:
        """Validate the arguments."""
        if not self.start_date and not self.end_date:
            msg = "Both start_date and end_date cannot be None."
            raise ValueError(msg)
        if not self.start_date:
            self.start_date = "1970-01-01"
        if not self.end_date:
            self.end_date = "2025-12-31"
        start_date_obj = (
            datetime.strptime(self.start_date, "%Y-%m-%d").replace(tzinfo=UTC).date()
        )
        end_date_obj = (
            datetime.strptime(self.end_date, "%Y-%m-%d").replace(tzinfo=UTC).date()
        )
        if start_date_obj > end_date_obj:
            msg = "start_date must be earlier than or equal to end_date."
            raise ValueError(msg)
        return self


class DateSearchEngineArguments(BaseSearchEngineArguments):
    """Arguments for date search engine."""

    date_ranges: list[DateRange] = Field(
        description="List of date ranges for the search engine.",
    )


class DateSearchResult(BaseSearchResult):
    """Result of date search."""


@spec_builder.search_engine("date_search")
class DateSearchEngine(BaseSearchEngine):
    """date search engine."""

    config: DateSearchEngineConfig

    def search(self, arguments: DateSearchEngineArguments) -> DateSearchResult:
        """Search for date values."""
        if not isinstance(arguments, DateSearchEngineArguments):
            msg = "Arguments must be DateSearchEngineArguments"
            raise TypeError(msg)
        return DateSearchResult()
