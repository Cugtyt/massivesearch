"""Base model."""

from abc import ABC, abstractmethod


class BaseModelClient(ABC):
    """Base class for all model clients."""

    @abstractmethod
    def response(self, messages: list, output_format: type) -> dict:
        """Get a response from the model."""
