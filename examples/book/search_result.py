"""Book search result."""  # noqa: INP001

import pandas as pd

from massivesearch.spec.base_search_engine import BaseSearchResult


class BookSearchResult(pd.DataFrame, BaseSearchResult):
    """Result of book text search."""
