"""Text Index Schema."""

from massivesearch.index.base import BaseIndex


class BasicTextIndex(BaseIndex):
    """Schema for text index."""

    examples: list[str]
