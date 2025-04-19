"""Number Index Schema."""

from pydantic import BaseModel

from massivesearch.index.base import BaseIndex


class NumberRange(BaseModel):
    """Range for number index."""

    min: float
    max: float


class BasicNumberIndex(BaseIndex):
    """Schema for number index."""

    range: NumberRange
    examples: list[float]

    def prompt(self) -> str:
        """Return the prompt for the index schema."""
        return "\n".join(
            [
                f"Description: {self.description}",
                f"Range: {self.range.min} to {self.range.max}",
                f"Examples: {self.examples}",
            ],
        )
