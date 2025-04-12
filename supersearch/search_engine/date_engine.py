"""Date search engine."""

from pydantic import BaseModel, Field

from supersearch.search_engine.base_engine import (
    BaseSearchEngine,
    BaseSearchEngineArguments,
    BaseSearchEngineConfig,
)
from supersearch.search_engine.hub import search_engine


class DateSearchEngineConfig(BaseSearchEngineConfig):
    """Config for date search engine."""

    format: str


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


class DateSearchEngineArguments(BaseSearchEngineArguments):
    """Arguments for date search engine."""

    date_ranges: list[DateRange] = Field(
        description="List of date ranges for the search engine.",
    )


@search_engine("date")
class DateSearchEngine(BaseSearchEngine):
    """date search engine."""

    config: DateSearchEngineConfig | None
    arguments: DateSearchEngineArguments | None = None
