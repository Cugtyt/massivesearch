"""Date Index Schema."""



from index.schema.base import BaseIndexSchema


class DateIndexSchema(BaseIndexSchema):
    """Schema for date index."""

    examples: list[str]
