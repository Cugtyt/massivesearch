"""Date Index Schema."""

from supersearch.index.schema.base import BaseIndexSchema
from supersearch.index.schema.hub import index_schema


@index_schema("date")
class DateIndexSchema(BaseIndexSchema):
    """Schema for date index."""

    examples: list[str]
