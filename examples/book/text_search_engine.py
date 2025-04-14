"""Book Text Search Engine."""  # noqa: INP001

from data_loader import load_data
from search_result import BookSearchResultIndex

from massivesearch.search_engine.text_engine import (
    TextSearchEngine,
    TextSearchEngineArguments,
    TextSearchEngineConfig,
)
from massivesearch.spec import SpecBuilder

book_builder = SpecBuilder()


class BookTextSearchConfig(TextSearchEngineConfig):
    """Config for book text search engine."""

    column_name: str


@book_builder.search_engine("book_text_search")
class BookTextSearch(TextSearchEngine):
    """Book text search engine."""

    config: BookTextSearchConfig

    def search(self, arguments: TextSearchEngineArguments) -> BookSearchResultIndex:
        """Search for book text values."""
        book_df = load_data()
        book_series_lower = book_df[self.config.column_name].str.lower()
        keywords_lower = [keyword.lower() for keyword in arguments.keywords]
        match self.config.matching_strategy:
            case "exact":
                indices = book_df.index[book_series_lower.isin(keywords_lower)]
            case "contains":
                indices = book_df.index[
                    book_series_lower.str.contains("|".join(keywords_lower))
                ]
            case "starts_with":
                indices = book_df.index[
                    book_series_lower.str.startswith(keywords_lower)
                ]
            case "ends_with":
                indices = book_df.index[book_series_lower.str.endswith(keywords_lower)]
            case _:
                msg = "Invalid matching strategy."
                raise ValueError(msg)

        return indices
