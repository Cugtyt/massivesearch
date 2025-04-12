"""Text Index Schema."""

from supersearch.index.schema.base import BaseIndexSchema
from supersearch.index.schema.hub import index_schema


@index_schema("text")
class TextIndexSchema(BaseIndexSchema):
    """Schema for text index."""

    examples: list[str]
