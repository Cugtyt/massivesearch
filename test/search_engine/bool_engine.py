"""Boolean search engine."""

from typing import Self

from pydantic import Field, model_validator

from massivesearch.search_engine.base import (
    BaseSearchEngine,
    BaseSearchEngineArguments,
    BaseSearchEngineConfig,
    BaseSearchResultIndex,
)
from massivesearch.spec import SpecBuilder

spec_builder = SpecBuilder()


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


@spec_builder.search_engine("boolean_search")
class BoolSearchEngine(BaseSearchEngine):
    """Boolean search engine."""

    config: BoolSearchEngineConfig

    def search(self, arguments: BoolSearchEngineArguments) -> BaseSearchResultIndex:
        """Search for boolean values."""
        msg = "Boolean search engine is not implemented yet."
        raise NotImplementedError(msg)
