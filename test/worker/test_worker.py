"""Tests for SpecBuilder."""

import json
from pathlib import Path

import yaml

from supersearch.model.azure_openai import AzureOpenAIClient
from supersearch.spec.builder import SpecBuilder
from supersearch.worker.worker import Worker


def test_worker_build_query() -> None:
    """Test worker build query."""
    spec_file_path = Path("./test/spec/test_spec.yaml")

    with spec_file_path.open() as file:
        valid_spec = yaml.safe_load(file)

    builder_from_file = SpecBuilder()
    builder_from_file.include(valid_spec)

    worker = Worker(
        spec=builder_from_file.spec,
        model_client=AzureOpenAIClient(temperature=0),
    )
    query_arguments = worker.build_query("for teens < $100")
    if not query_arguments:
        msg = "Query should not be empty."
        raise ValueError(msg)
    if not isinstance(query_arguments, list):
        msg = "Query should be a dictionary."
        raise TypeError(msg)
    if "Teens" not in query_arguments[0]["target_audience"]["keywords"]:
        msg = "Expected 'Teens' to be in the query."
        raise ValueError(msg)


def test_worker_build_complex_query() -> None:
    """Test querying with SpecBuilder."""
    spec_file_path = Path("./test/spec/test_spec.yaml")

    with spec_file_path.open() as file:
        valid_spec = yaml.safe_load(file)

    builder_from_file = SpecBuilder()
    builder_from_file.include(valid_spec)
    worker = Worker(
        spec=builder_from_file.spec,
        model_client=AzureOpenAIClient(temperature=0),
    )
    query_arguments = worker.build_query(
        "I want to buy a book for white snow, I only have $10, I am 10 years old, "
        "I want the book in English and produced after 2020",
    )
    if not query_arguments:
        msg = "Query should not be empty."
        raise ValueError(msg)
    if not isinstance(query_arguments, list):
        msg = "Query should be a dictionary."
        raise TypeError(msg)

    query_to_string = json.dumps(query_arguments, indent=2)
    if "snow" not in query_to_string:
        msg = "Expected 'snow' to be in the query."
        raise ValueError(msg)
    if "10" not in query_to_string:
        msg = "Expected '10' to be in the query."
        raise ValueError(msg)
    if "English" not in query_to_string:
        msg = "Expected 'English' to be in the query."
        raise ValueError(msg)
    if "2020" not in query_to_string:
        msg = "Expected '2020' to be in the query."
        raise ValueError(msg)
    if "white" not in query_to_string:
        msg = "Expected 'white' to be in the query."
        raise ValueError(msg)
    if "book" not in query_to_string:
        msg = "Expected 'book' to be in the query."
        raise ValueError(msg)
