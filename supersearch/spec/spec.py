"""Spec."""

from pydantic import BaseModel

from supersearch.index.base import BaseIndex
from supersearch.search_engine.base_engine import BaseSearchEngine


class Spec(BaseModel):
    """Spec class."""

    index_spec: dict[str, BaseIndex]
    search_engine_spec: dict[str, BaseSearchEngine]

    prompt_message: str
    format_model: type[BaseModel]
