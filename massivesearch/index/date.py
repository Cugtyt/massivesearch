"""Date Index Schema."""

from massivesearch.spec import BaseIndex, SpecBuilder

spec_builder = SpecBuilder()


@spec_builder.index("date_index")
class DateIndex(BaseIndex):
    """Schema for date index."""

    examples: list[str]
