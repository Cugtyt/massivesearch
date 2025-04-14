"""Book search result."""  # noqa: INP001

import pandas as pd

from supersearch.spec.base_search_engine import BaseSearchResult


class BookSearchResult(BaseSearchResult):
    """Result of book text search."""

    def __init__(self, result: pd.DataFrame) -> None:
        """Initialize book search result."""
        super().__init__()
        self.result = result
