"""Number search engine."""

from pydantic import BaseModel, Field

from supersearch.search_engine.base_engine import (
    BaseSearchEngine,
    BaseSearchEngineArguments,
    BaseSearchEngineConfig,
)
from supersearch.search_engine.hub import search_engine


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


class NumberSearchEngineArguments(BaseSearchEngineArguments):
    """Arguments for number search engine."""

    number_ranges: list[NumberRange] = Field(
        description="List of number ranges for the search engine.",
    )


@search_engine("number")
class NumberSearchEngine(BaseSearchEngine):
    """Number search engine."""

    config: NumberSearchEngineConfig | None = None
    arguments: NumberSearchEngineArguments | None = None
