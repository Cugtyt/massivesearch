"""Book search example."""  # noqa: INP001

import logging
from pathlib import Path

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
    """Book text index.

    The decorator is working same as the following code:
    ```python
    book_builder.register_index("text_index", BasicTextIndex)
    ```
    """


@book_builder.index("number_index")
class BookPriceIndex(BasicNumberIndex):
    """Book price index.

    The decorator is working same as the following code:
    ```python
    book_builder.register_index("number_index", BasicNumberIndex)
    ```
    """


@book_builder.search_engine("book_text_search")
class BookTextSearchEngine(PandasTextSearchEngine):
    """Book text search engine.

    The decorator is working same as the following code:
    ```python
    book_builder.register_search_engine("book_text_search", PandasTextSearchEngine)
    ```
    """


@book_builder.search_engine("book_price_search")
class BookPriceSearchEngine(PandasNumberSearchEngine):
    """Book price search engine.

    The decorator is working same as the following code:
    ```python
    book_builder.register_search_engine("book_price_search", PandasNumberSearchEngine)
    ```
    """


book_builder.register_aggregator_type(
    "book_aggregator",
    PandasAggregator,
)
book_builder.register_ai_client_type(
    "azure_openai",
    AzureOpenAIClient,
)


def main() -> None:
    """Run the book search example."""
    with Path("./examples/book/book_spec.yaml").open() as file:
        spec_file = yaml.safe_load(file)

    book_builder.include(spec_file)
    worker = Worker(book_builder.spec)
    agg_result = worker.execute(
        "I want to buy a book about prince or lord, I only have 30 dollars.",
    )

    logger.info("Search query:")
    for result in worker.last_search_query:
        logger.info(result)

    logger.info("Books:")
    logger.info(agg_result)


if __name__ == "__main__":
    main()
