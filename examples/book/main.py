"""Book search example."""  # noqa: INP001

import functools
import logging
from pathlib import Path

import pandas as pd
import yaml

from massivesearch.ext.pandas.aggregator import PandasAggregator
from massivesearch.ext.pandas.number import PandasNumberSearchEngine
from massivesearch.ext.pandas.text import PandasTextSearchEngine
from massivesearch.index.number import BasicNumberIndex
from massivesearch.index.text import BasicTextIndex
from massivesearch.model.azure_openai import AzureOpenAIClient
from massivesearch.spec import SpecBuilder
from massivesearch.worker import Worker

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


book_builder = SpecBuilder()


@book_builder.index("text_index")
class BookTextIndex(BasicTextIndex):
    """Book text index."""


@book_builder.index("number_index")
class BookPriceIndex(BasicNumberIndex):
    """Book price index."""


@functools.lru_cache(maxsize=1)
def load_df() -> pd.DataFrame:
    """Load book data from a CSV file. Caches the result."""
    file_path: str = "examples/book/books.csv"
    logger.info("Loading data from %s...", file_path)
    return pd.read_csv(file_path)


class BookDataMixin:
    """Mixin class to provide book data loading."""

    def load_df(self) -> pd.DataFrame:
        """Load book data using the cached function."""
        return load_df()


@book_builder.search_engine("book_text_search")
class BookTextSearchEngine(BookDataMixin, PandasTextSearchEngine):
    """Book text search engine."""


@book_builder.search_engine("book_price_search")
class BookPriceSearchEngine(BookDataMixin, PandasNumberSearchEngine):
    """Book price search engine."""


class BookAggregator(BookDataMixin, PandasAggregator):
    """Book aggregator."""


def main() -> None:
    """Run the book search example."""
    with Path("./examples/book/book_spec.yaml").open() as file:
        spec_file = yaml.safe_load(file)

    book_builder.include(spec_file)
    worker = Worker(
        book_builder.spec,
        model_client=AzureOpenAIClient(temperature=0),
    )
    execute_results = worker.execute(
        "I want to buy a book about prince or lord, and I only have 20 dollars.",
    )

    logger.info("Search query:")
    for result in execute_results:
        logger.info(result.query)

    aggregator = BookAggregator()
    agg_result = aggregator.aggregate(execute_results)
    logger.info("Books:")
    logger.info(agg_result)


if __name__ == "__main__":
    main()
