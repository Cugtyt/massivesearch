"""Boolean Index Schema."""

from supersearch.index.base import BaseIndex
from supersearch.index.hub import index


@index("boolean_index")
class BoolIndex(BaseIndex):
    """Schema for boolean index."""
