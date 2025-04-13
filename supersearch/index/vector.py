"""Vector Index Schema."""

from supersearch.index.base import BaseIndex
from supersearch.index.hub import index


@index("vector_index")
class VectorIndex(BaseIndex):
    """Schema for vector index."""
