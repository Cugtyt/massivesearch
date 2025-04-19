"""Pipe Index Unit."""

from pydantic import BaseModel

from massivesearch.index.base import BaseIndex
from massivesearch.search_engine.base import BaseSearchEngine


class MassiveSearchIndex(BaseModel):
    """MassiveSearch index unit."""

    name: str
    index: BaseIndex
    search_engine: BaseSearchEngine
    search_engine_arguments_type: type[BaseModel]

    def prompt(self) -> str:
        """Get the prompt message."""
        return self.index.prompt(self.name)
