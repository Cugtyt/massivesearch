"""Base model."""

from abc import ABC, abstractmethod

from pydantic import BaseModel


class BaseAIClient(BaseModel, ABC):
    """Base class for all model clients."""

    @abstractmethod
    def response(self, messages: list, output_format: type[BaseModel]) -> dict:
        """Get a response from the model."""
