"""Text Index Schema."""


from index.schema.base import BaseIndexSchema


class TextIndexSchema(BaseIndexSchema):
    """Schema for text index."""

    examples: list[str]
