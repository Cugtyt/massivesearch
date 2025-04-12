"""Boolean Index Schema."""

from supersearch.index.schema.base import BaseIndexSchema
from supersearch.index.schema.hub import index_schema


@index_schema("boolean")
class BoolIndexSchema(BaseIndexSchema):
    """Schema for boolean index."""
