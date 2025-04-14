"""Base Index Schema."""

from abc import ABC

from pydantic import BaseModel


class BaseIndex(BaseModel, ABC):
    """Base class for index schemas."""

    description: str
    examples: list | None = None

    def prompt(self, index_name: str) -> str:
        """Return the prompt for the index schema."""
        return "\n".join(
            [
                f"Index Name: {index_name}",
                f"Description: {self.description}",
                f"Examples: {self.examples}" if self.examples else "",
            ],
        )
