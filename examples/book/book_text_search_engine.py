"""Book Text Search Engine."""  # noqa: INP001

import pandas as pd
from book_search_result import BookSearchResult

from supersearch.search_engine.text_engine import (
    TextSearchEngine,
    TextSearchEngineArguments,
    TextSearchEngineConfig,
)
from supersearch.spec import SpecBuilder

book_builder = SpecBuilder()


class BookTextSearchConfig(TextSearchEngineConfig):
    """Config for book text search engine."""

    file_path: str = "examples/book/books.csv"
    column_name: str


@book_builder.search_engine("book_text_search")
class BookTextSearch(TextSearchEngine):
    """Book text search engine."""

    config: BookTextSearchConfig

    def search(self, arguments: TextSearchEngineArguments) -> BookSearchResult:
        """Search for book text values."""
        book_df = pd.read_csv(self.config.file_path)
        book_df = book_df[self.config.column_name]
        book_series_lower = book_df.str.lower()
        keywords_lower = [keyword.lower() for keyword in arguments.keywords]
        match self.config.matching_strategy:
            case "exact":
                result = book_df[book_series_lower.isin(keywords_lower)]
            case "contains":
                result = book_df[
                    book_series_lower.str.contains("|".join(keywords_lower))
                ]
            case "starts_with":
                result = book_df[
                    book_series_lower.str.startswith(keywords_lower)
                ]
            case "ends_with":
                result = book_df[
                    book_series_lower.str.endswith(keywords_lower)
                ]
            case _:
                msg = "Invalid matching strategy."
                raise ValueError(msg)

        return BookSearchResult(result=result)
