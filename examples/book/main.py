"""Book search example."""  # noqa: INP001

import logging
from pathlib import Path

import yaml
from aggregate import BookAggregator
from price_search_engine import (
    book_builder as book_price_search_builder,
)
from text_search_engine import (
    book_builder as book_text_search_builder,
)

from massivesearch.index import number_index_spec_builder, text_index_spec_builder
from massivesearch.model.azure_openai import AzureOpenAIClient
from massivesearch.worker import Worker

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main() -> None:
    """Run the book search example."""
    book_builder = (
        book_text_search_builder
        | book_price_search_builder
        | text_index_spec_builder
        | number_index_spec_builder
    )
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

    aggregator = BookAggregator()
    agg_result = aggregator.aggregate(execute_results)
    logger.info("Books:")
    logger.info(agg_result.books)


if __name__ == "__main__":
    main()
