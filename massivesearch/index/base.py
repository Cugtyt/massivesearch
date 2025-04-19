"""Base Index Schema."""

from abc import ABC

from pydantic import BaseModel, ConfigDict


class BaseIndex(BaseModel, ABC):
    """Base class for index schemas."""

    model_config = ConfigDict(extra="ignore")

    description: str
    examples: list

    def prompt(self) -> str:
        """Return the prompt for the index schema."""
        return "\n".join(
            [
                f"Description: {self.description}",
                f"Examples: {self.examples}" if self.examples else "",
            ],
        )
