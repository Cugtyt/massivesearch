"""Book Price Search Engine."""  # noqa: INP001

import operator
from functools import reduce

from data_loader import load_data
from search_result import BookSearchResultIndex

from massivesearch.search_engine.number_engine import (
    NumberSearchEngine,
    NumberSearchEngineArguments,
)
from massivesearch.spec import BaseSearchEngineConfig, SpecBuilder

book_builder = SpecBuilder()


class BookPriceSearchConfig(BaseSearchEngineConfig):
    """Config for book price search engine."""

    column_name: str


@book_builder.search_engine("book_price_search")
class BookTextSearch(NumberSearchEngine):
    """Book text search engine."""

    config: BookPriceSearchConfig

    def search(self, arguments: NumberSearchEngineArguments) -> BookSearchResultIndex:
        """Search for book text values within any of the specified ranges."""
        book_df = load_data()
        book_price_series = book_df[self.config.column_name]

        masks = []

        for number_range in arguments.number_ranges:
            start_number = number_range.start_number
            end_number = number_range.end_number
            if start_number is not None and end_number is not None:
                current_mask = (book_price_series >= start_number) & (
                    book_price_series <= end_number
                )
            elif start_number is not None:
                current_mask = book_price_series >= start_number
            elif end_number is not None:
                current_mask = book_price_series <= end_number
            else:
                continue
            masks.append(current_mask)

        if not masks:
            return book_df.index
        combined_mask = reduce(operator.or_, masks)
        return book_df[combined_mask].index
