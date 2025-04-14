"""Book Price Search Engine."""  # noqa: INP001

import operator
from functools import reduce

import pandas as pd
from search_result import BookSearchResult

from massivesearch.search_engine.number_engine import (
    NumberSearchEngine,
    NumberSearchEngineArguments,
)
from massivesearch.spec import BaseSearchEngineConfig, SpecBuilder

book_builder = SpecBuilder()


class BookPriceSearchConfig(BaseSearchEngineConfig):
    """Config for book price search engine."""

    file_path: str = "examples/book/books.csv"
    column_name: str


@book_builder.search_engine("book_price_search")
class BookTextSearch(NumberSearchEngine):
    """Book text search engine."""

    config: BookPriceSearchConfig

    def search(self, arguments: NumberSearchEngineArguments) -> BookSearchResult:
        """Search for book text values within any of the specified ranges."""
        book_df = pd.read_csv(self.config.file_path)
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
            final_result_df = book_df.iloc[0:0]
        else:
            combined_mask = reduce(operator.or_, masks)
            final_result_df = book_df[combined_mask]

        return final_result_df
