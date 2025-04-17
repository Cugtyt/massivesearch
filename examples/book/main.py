"""Book search example."""  # noqa: INP001

import logging

from massivesearch.ext.pandas.aggregator import PandasAggregator
from massivesearch.ext.pandas.number import PandasNumberSearchEngine
from massivesearch.ext.pandas.text import PandasTextSearchEngine
from massivesearch.index.number import BasicNumberIndex
from massivesearch.index.text import BasicTextIndex
from massivesearch.model.azure_openai import AzureOpenAIClient
from massivesearch.pipe.pipe import MassiveSearchPipe

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


book_msp = MassiveSearchPipe()


@book_msp.index_type("text_index")
class BookTextIndex(BasicTextIndex):
    """Book text index.

    The decorator is working same as the following code:
    ```python
    book_msp.register_index_type("text_index", BasicTextIndex)
    ```
    """


@book_msp.index_type("number_index")
class BookPriceIndex(BasicNumberIndex):
    """Book price index.

    The decorator is working same as the following code:
    ```python
    book_msp.register_index_type("number_index", BasicNumberIndex)
    ```
    """


@book_msp.search_engine_type("book_text_search")
class BookTextSearchEngine(PandasTextSearchEngine):
    """Book text search engine.

    The decorator is working same as the following code:
    ```python
    book_msp.register_search_engine_type("book_text_search", PandasTextSearchEngine)
    ```
    """


@book_msp.search_engine_type("book_price_search")
class BookPriceSearchEngine(PandasNumberSearchEngine):
    """Book price search engine.

    The decorator is working same as the following code:
    ```python
    book_msp.register_search_engine_type("book_price_search", PandasNumberSearchEngine)
    ```
    """


book_msp.register_aggregator_type(
    "book_aggregator",
    PandasAggregator,
)
book_msp.register_ai_client_type(
    "azure_openai",
    AzureOpenAIClient,
)


async def main() -> None:
    """Run the book search example."""
    book_msp.build_from_file("./examples/book/book_spec.yaml")
    result = await book_msp.run(
        "I want to buy a book about prince or lord, I only have 30 dollars.",
    )

    logger.info("Search query:")
    for q in book_msp.serach_query:
        logger.info(q)

    logger.info("Books:")
    logger.info(result)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
