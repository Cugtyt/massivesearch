"""Book search result."""  # noqa: INP001

from dataclasses import dataclass

import pandas as pd

from supersearch.spec.base_search_engine import BaseSearchResult


@dataclass
class BookSearchResult(BaseSearchResult):
    """Result of book text search."""

    result: pd.DataFrame
