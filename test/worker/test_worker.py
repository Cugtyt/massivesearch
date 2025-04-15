"""Tests for SpecBuilder."""

import json
from pathlib import Path
from unittest.mock import MagicMock

import pytest
import yaml

from massivesearch.model.azure_openai import AzureOpenAIClient
from massivesearch.spec.validator import SpecSchemaError
from massivesearch.worker import Worker
from test.aggregator import TestAggregator
from test.index import (
    bool_index_spec_builder,
    date_index_spec_builder,
    number_index_spec_builder,
    text_index_spec_builder,
    vector_index_spec_builder,
)
from test.search_engine import (
    bool_search_engine_spec_builder,
    date_search_engine_spec_builder,
    number_search_engine_spec_builder,
    text_search_engine_spec_builder,
    vector_search_engine_spec_builder,
)


def test_worker_build_query() -> None:
    """Test worker build query."""
    spec_file_path = Path("./test/spec/test_spec.yaml")

    with spec_file_path.open() as file:
        valid_spec = yaml.safe_load(file)

    builder = (
        bool_index_spec_builder
        | date_index_spec_builder
        | number_index_spec_builder
        | text_index_spec_builder
        | vector_index_spec_builder
        | bool_search_engine_spec_builder
        | date_search_engine_spec_builder
        | number_search_engine_spec_builder
        | text_search_engine_spec_builder
        | vector_search_engine_spec_builder
    )
    with pytest.raises(SpecSchemaError):
        builder.include(valid_spec)

    builder.register_aggregator_type("test_aggregator", TestAggregator)
    builder.include(valid_spec)

    builder.set_aggregator_spec(
        aggregator_type="test_aggregator",
        aggregator_arguments={},
    )

    worker = Worker(
        spec=builder.spec,
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

    builder = (
        bool_index_spec_builder
        | date_index_spec_builder
        | number_index_spec_builder
        | text_index_spec_builder
        | vector_index_spec_builder
        | bool_search_engine_spec_builder
        | date_search_engine_spec_builder
        | number_search_engine_spec_builder
        | text_search_engine_spec_builder
        | vector_search_engine_spec_builder
    )
    builder.register_aggregator_type("test_aggregator", TestAggregator)
    builder.include(valid_spec)

    builder.set_aggregator_spec(
        aggregator_type="test_aggregator",
        aggregator_arguments={},
    )
    worker = Worker(
        spec=builder.spec,
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


def test_worker_execute() -> None:
    """Test worker execute."""
    spec_file_path = Path("./test/spec/test_spec.yaml")

    with spec_file_path.open() as file:
        valid_spec = yaml.safe_load(file)

    builder = (
        bool_index_spec_builder
        | date_index_spec_builder
        | number_index_spec_builder
        | text_index_spec_builder
        | vector_index_spec_builder
        | bool_search_engine_spec_builder
        | date_search_engine_spec_builder
        | number_search_engine_spec_builder
        | text_search_engine_spec_builder
        | vector_search_engine_spec_builder
    )
    builder.register_aggregator_type("test_aggregator", TestAggregator)
    builder.include(valid_spec)

    builder.set_aggregator_spec(
        aggregator_type="test_aggregator",
        aggregator_arguments={},
    )
    fake_model_client = MagicMock()
    fake_model_client.response.return_value = {
        "queries": [],
    }

    worker = Worker(
        spec=builder.spec,
        model_client=fake_model_client,
    )

    result = worker.execute("test")
    if result is not True:
        msg = "Expected True, got {result}."
        raise ValueError(msg.format(result=result))
