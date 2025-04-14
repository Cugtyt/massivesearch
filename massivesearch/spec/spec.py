"""Spec."""

from pydantic import BaseModel

from massivesearch.spec.base_index import BaseIndex
from massivesearch.spec.base_search_engine import (
    BaseSearchEngine,
    BaseSearchEngineArguments,
)


class SpecUnit(BaseModel):
    """Spec unit class."""

    index: BaseIndex
    search_engine: BaseSearchEngine
    search_engine_arguments_type: type[BaseSearchEngineArguments]


class Spec(BaseModel):
    """Spec class."""

    items: dict[str, SpecUnit]

    prompt_message: str
    query_model: type[BaseModel]
