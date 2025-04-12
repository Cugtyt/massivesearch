"""Number Index Schema."""


from pydantic import BaseModel

from index.schema.base import BaseIndexSchema


class NumberRange(BaseModel):
    """Range for number index."""

    min: float
    max: float

class NumberIndexSchema(BaseIndexSchema):
    """Schema for number index."""

    range: NumberRange
    examples: list[float]
