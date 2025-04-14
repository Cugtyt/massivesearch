"""Number Index Schema."""

from pydantic import BaseModel

from massivesearch.spec import BaseIndex, SpecBuilder

spec_builder = SpecBuilder()


class NumberRange(BaseModel):
    """Range for number index."""

    min: float
    max: float


@spec_builder.index("number_index")
class NumberIndex(BaseIndex):
    """Schema for number index."""

    range: NumberRange
    examples: list[float]

    def prompt(self, index_name: str) -> str:
        """Return the prompt for the index schema."""
        return "\n".join(
            [
                f"Index Name: {index_name}",
                f"Description: {self.description}",
                f"Range: {self.range.min} to {self.range.max}",
                f"Examples: {self.examples}",
            ],
        )
