"""Date Index Schema."""

from supersearch.spec import BaseIndex, SpecBuilder

spec_builder = SpecBuilder()


@spec_builder.index("date_index")
class DateIndex(BaseIndex):
    """Schema for date index."""

    examples: list[str]
