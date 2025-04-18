"""Base model."""

from abc import ABC, abstractmethod

from pydantic import BaseModel


class BaseAIClient(BaseModel, ABC):
    """Base class for all model clients."""

    @abstractmethod
    async def response(self, messages: list, format_model: type[BaseModel]) -> dict:
        """Get a response from the model."""
