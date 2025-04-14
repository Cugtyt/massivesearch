"""Vector Index Schema."""

from supersearch.spec import BaseIndex, SpecBuilder

spec_builder = SpecBuilder()

@spec_builder.index("vector_index")
class VectorIndex(BaseIndex):
    """Schema for vector index."""
