"""Vector Index Schema."""

from massivesearch.spec import BaseIndex, SpecBuilder

spec_builder = SpecBuilder()


@spec_builder.index("vector_index")
class VectorIndex(BaseIndex):
    """Schema for vector index."""
