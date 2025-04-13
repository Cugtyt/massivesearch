"""Number Index Schema."""

from pydantic import BaseModel

from supersearch.index.schema.base import BaseIndexSchema
from supersearch.index.schema.hub import index_schema


class NumberRange(BaseModel):
    """Range for number index."""

    min: float
    max: float


@index_schema("number")
class NumberIndexSchema(BaseIndexSchema):
    """Schema for number index."""

    range: NumberRange
    examples: list[float]

    def schema_prompt(self, index_name: str) -> str:
        """Return the prompt for the index schema."""
        return "\n".join(
            [
                f"Index Name: {index_name}",
                f"Description: {self.description}",
                f"Range: {self.range.min} to {self.range.max}",
                f"Examples: {self.examples}",
            ],
        )
