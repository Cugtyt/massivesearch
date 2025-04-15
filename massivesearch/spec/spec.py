"""Spec."""

from pydantic import BaseModel

from massivesearch.aggregator.base import BaseAggregator
from massivesearch.index.base import BaseIndex
from massivesearch.model.base import BaseAIClient
from massivesearch.search_engine.base import (
    BaseSearchEngine,
    BaseSearchEngineArguments,
)


class SpecIndexUnit(BaseModel):
    """Spec unit class."""

    index: BaseIndex
    search_engine: BaseSearchEngine
    search_engine_arguments_type: type[BaseSearchEngineArguments]


class Spec(BaseModel):
    """Spec class."""

    indexs: dict[str, SpecIndexUnit]
    aggregator: BaseAggregator

    prompt_message: str
    query_model: type[BaseModel]

    ai_client: BaseAIClient
