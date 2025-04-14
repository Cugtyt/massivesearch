"""Book search example."""  # noqa: INP001

from pathlib import Path

import yaml
from book_price_search_engine import (
    book_builder as book_price_search_builder,
)
from book_text_search_engine import (
    book_builder as book_text_search_builder,
)

from supersearch.index import number_index_spec_builder, text_index_spec_builder
from supersearch.model.azure_openai import AzureOpenAIClient
from supersearch.worker import Worker


def main():
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

    for execute_result in execute_results:
        print(f"Query: {execute_result.query}")
        print()

        for name, result in execute_result.result.items():
            print("Searching for:", name)
            print("Result:")
            print(result.result)

            print("-" * 80)


if __name__ == "__main__":
    main()
