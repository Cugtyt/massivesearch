"""Base Index Schema."""

from abc import ABC

from pydantic import BaseModel

from supersearch.search_engine.base_engine import BaseSearchEngine


class BaseIndexSchema(BaseModel, ABC):
    """Base class for index schemas."""

    description: str
    examples: list | None = None
    search_engine: BaseSearchEngine
