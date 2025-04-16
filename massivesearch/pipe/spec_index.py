"""Pipe Index Unit."""

from pydantic import BaseModel

from massivesearch.index.base import BaseIndex
from massivesearch.search_engine.base import BaseSearchEngine, BaseSearchEngineArguments


class SpecIndex(BaseModel):
    """Spec unit class."""

    name: str
    index: BaseIndex
    search_engine: BaseSearchEngine
    search_engine_arguments_type: type[BaseSearchEngineArguments]

    def prompt(self) -> str:
        """Get the prompt message."""
        return self.index.prompt(self.name)
