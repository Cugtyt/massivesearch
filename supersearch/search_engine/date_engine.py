"""Date search engine."""

from datetime import datetime
from typing import Self

from pydantic import BaseModel, Field, model_validator

from supersearch.search_engine.base_engine import (
    BaseSearchEngine,
    BaseSearchEngineArguments,
    BaseSearchEngineConfig,
    BaseSearchResult,
)
from supersearch.search_engine.hub import search_engine


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
        start_date_obj = (
            datetime.strptime(self.start_date, "%Y-%m-%d")
            .replace(tzinfo=datetime.timezone.utc)
            .date()
        )
        end_date_obj = (
            datetime.strptime(self.end_date, "%Y-%m-%d")
            .replace(tzinfo=datetime.timezone.utc)
            .date()
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


@search_engine("date")
class DateSearchEngine(BaseSearchEngine):
    """date search engine."""

    config: DateSearchEngineConfig

    def search(self, arguments: DateSearchEngineArguments) -> DateSearchResult:
        """Search for date values."""
        if not isinstance(arguments, DateSearchEngineArguments):
            msg = "Arguments must be DateSearchEngineArguments"
            raise TypeError(msg)
        return DateSearchResult()
