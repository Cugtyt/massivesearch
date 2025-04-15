"""Boolean Index Schema."""

from massivesearch.spec import BaseIndex, SpecBuilder

spec_builder = SpecBuilder()


@spec_builder.index("boolean_index")
class BoolIndex(BaseIndex):
    """Schema for boolean index."""
