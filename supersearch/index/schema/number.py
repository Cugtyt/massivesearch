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
