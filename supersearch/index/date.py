"""Date Index Schema."""

from supersearch.index.base import BaseIndex
from supersearch.index.hub import index


@index("date_index")
class DateIndex(BaseIndex):
    """Schema for date index."""

    examples: list[str]
