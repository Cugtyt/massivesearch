"""Boolean search engine."""

from typing import Self

from pydantic import Field, model_validator

from supersearch.search_engine.base_engine import (
    BaseSearchEngine,
    BaseSearchEngineArguments,
    BaseSearchEngineConfig,
    BaseSearchResult,
)
from supersearch.search_engine.hub import search_engine


class BoolSearchEngineConfig(BaseSearchEngineConfig):
    """Config for boolean search engines."""

    true_value: str = "true"
    false_value: str = "false"


class BoolSearchEngineArguments(BaseSearchEngineArguments):
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


class BoolSearchResult(BaseSearchResult):
    """Result of boolean search."""


@search_engine("boolean")
class BoolSearchEngine(BaseSearchEngine):
    """Boolean search engine."""

    config: BoolSearchEngineConfig

    def search(self, arguments: BoolSearchEngineArguments) -> BoolSearchResult:
        """Search for boolean values."""
        if not isinstance(arguments, BoolSearchEngineArguments):
            msg = "Arguments must be BoolSearchEngineArguments"
            raise TypeError(msg)
        return BoolSearchResult()
