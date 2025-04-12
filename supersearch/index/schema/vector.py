"""Vector Index Schema."""

from supersearch.index.schema.base import BaseIndexSchema
from supersearch.index.schema.hub import index_schema


@index_schema("vector")
class VectorIndexSchema(BaseIndexSchema):
    """Schema for vector index."""
