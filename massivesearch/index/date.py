"""Date Index Schema."""

from massivesearch.index.base import BaseIndex


class BasicDateIndex(BaseIndex):
    """Schema for date index."""

    examples: list[str]
