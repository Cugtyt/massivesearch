"""Book search result."""  # noqa: INP001

import pandas as pd

from massivesearch.spec.base_search_engine import BaseSearchResultIndex


class BookSearchResultIndex(pd.Index, BaseSearchResultIndex):
    """Result of book text search."""
