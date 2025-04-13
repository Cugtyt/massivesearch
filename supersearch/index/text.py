"""Text Index Schema."""

from supersearch.index.base import BaseIndex
from supersearch.index.hub import index


@index("text_index")
class TextIndex(BaseIndex):
    """Schema for text index."""

    examples: list[str]
