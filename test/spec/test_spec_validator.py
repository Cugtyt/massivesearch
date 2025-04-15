"""Tests for validating spec files."""

from pathlib import Path

import pytest
import yaml

from massivesearch.spec import (
    SpecSchemaError,
    spec_validator,
)
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


def test_spec_validator_valid() -> None:
    """Test spec_validator with valid data."""
    with Path("./test/spec/test_spec.yaml").open() as file:
        valid_spec = yaml.safe_load(file)

    try:
        spec_validator(
            valid_spec,
            builder.registered_indexs,
            builder.registered_search_engines,
            builder.registered_aggregators,
        )
    except SpecSchemaError as e:
        pytest.fail(f"spec_validator raised an unexpected exception: {e}")


def test_spec_validator_missing_index_key() -> None:
    """Test spec_validator when the 'index' key is missing."""
    invalid_spec = {
        "description": {  # Incorrect top-level key
            "type": "text_index",
            "description": "A detailed description of the product.",
            "examples": ["example1", "example2"],
            "search_engine": {"type": "text_search"},
        },
    }
    with pytest.raises(
        SpecSchemaError,
        match="Spec 'indexs': Indexs spec is missing.",
    ):
        spec_validator(
            invalid_spec,
            builder.registered_indexs,
            builder.registered_search_engines,
            builder.registered_aggregators,
        )


def test_spec_validator_index_not_list() -> None:
    """Test spec_validator when 'index' is not a list."""
    invalid_spec = {
        "indexs": {  # Should be a list
            "name": "description",
            "type": "text_index",
            "search_engine": {"type": "text_search"},
        },
    }
    with pytest.raises(
        SpecSchemaError,
        match="Spec 'indexs': Indexs spec must be a list.",
    ):
        spec_validator(
            invalid_spec,
            builder.registered_indexs,
            builder.registered_search_engines,
            builder.registered_aggregators,
        )


def test_spec_validator_missing_index_name() -> None:
    """Test spec_validator with a missing index name."""
    invalid_spec = {
        "indexs": [
            {
                # "name": "description", # Name is missing  # noqa: ERA001
                "type": "text_index",
                "search_engine": {"type": "text_search"},
            },
        ],
    }
    with pytest.raises(
        SpecSchemaError,
        match="Spec 'None': Index name is missing.",
    ):
        spec_validator(
            invalid_spec,
            builder.registered_indexs,
            builder.registered_search_engines,
            builder.registered_aggregators,
        )


def test_spec_validator_missing_index_type() -> None:
    """Test spec_validator with a missing index type."""
    invalid_spec = {
        "indexs": [
            {
                "name": "description",
                # "type": "text_index", # Type is missing  # noqa: ERA001
                "search_engine": {"type": "text_search"},
            },
        ],
    }
    with pytest.raises(
        SpecSchemaError,
        match="Spec 'description': Index type is missing.",
    ):
        spec_validator(
            invalid_spec,
            builder.registered_indexs,
            builder.registered_search_engines,
            builder.registered_aggregators,
        )


def test_spec_validator_unknown_index_type() -> None:
    """Test spec_validator with an unknown index type."""
    invalid_spec = {
        "indexs": [
            {
                "name": "description",
                "type": "text_index",  # Valid
                "search_engine": {"type": "text_search"},
            },
            {
                "name": "price",
                "description": "The price of the product.",
                "search_engine": {"type": "number_search"},
            },
        ],
    }

    with pytest.raises(
        SpecSchemaError,
        match="Spec 'description': Index 'description' validation failed",
    ):
        spec_validator(
            invalid_spec,
            builder.registered_indexs,
            builder.registered_search_engines,
            builder.registered_aggregators,
        )


def test_spec_validator_missing_search_engine() -> None:
    """Test spec_validator with a missing search_engine key."""
    invalid_spec = {
        "indexs": [
            {
                "name": "description",
                "type": "text_index",
                # "search_engine": {"type": "text_search"}, # Missing  # noqa: ERA001
            },
        ],
    }
    with pytest.raises(
        SpecSchemaError,
        match="Spec 'description': Index 'description' validation failed",
    ):
        spec_validator(
            invalid_spec,
            builder.registered_indexs,
            builder.registered_search_engines,
            builder.registered_aggregators,
        )


def test_spec_validator_missing_search_engine_type() -> None:
    """Test spec_validator with a missing search engine type."""
    invalid_spec = {
        "indexs": [
            {
                "name": "description",
                "type": "text_index",
                "search_engine": {
                    # "type": "text_search", # Missing  # noqa: ERA001
                },
            },
        ],
    }
    with pytest.raises(
        SpecSchemaError,
        match="Spec 'description': Index 'description' validation failed",
    ):
        spec_validator(
            invalid_spec,
            builder.registered_indexs,
            builder.registered_search_engines,
            builder.registered_aggregators,
        )


def test_spec_validator_unknown_search_engine_type() -> None:
    """Test spec_validator with an unknown search engine type."""
    invalid_spec = {
        "indexs": [
            {
                "name": "description",
                "type": "text_index",
                "description": "A detailed description of the product.",
                "search_engine": {
                    "type": "unknown_engine",  # Invalid type
                },
            },
        ],
    }

    with pytest.raises(
        SpecSchemaError,
        match="Spec 'description': Index 'description' validation failed",
    ):
        spec_validator(
            invalid_spec,
            builder.registered_indexs,
            builder.registered_search_engines,
            builder.registered_aggregators,
        )


def test_spec_validator_invalid_index_schema() -> None:
    """Test spec_validator with an invalid index schema (Pydantic error)."""
    invalid_spec = {
        "indexs": [
            {
                "name": "price",
                "type": "number_index",
                "description": "The price of the product.",
                "range": {
                    "min": "not a number",  # Invalid type for min
                    "max": 10000,
                },
                "search_engine": {
                    "type": "number_search",
                },
            },
        ],
    }
    with pytest.raises(
        SpecSchemaError,
        match="Spec 'price': Index 'price' validation failed for 'number_index':",
    ):
        spec_validator(
            invalid_spec,
            builder.registered_indexs,
            builder.registered_search_engines,
            builder.registered_aggregators,
        )


def test_spec_validator_invalid_search_engine_schema() -> None:
    """Test spec_validator with an invalid search engine schema (Pydantic error)."""
    invalid_spec = {
        "indexs": [
            {
                "name": "image",
                "type": "vector_index",
                "description": "Product images",
                "search_engine": {
                    "type": "vector_search",
                    "top_k": "not a number",  # Invalid type for top_k
                    "distance_metric": "cosine",
                },
            },
        ],
    }

    with pytest.raises(
        SpecSchemaError,
        match="Spec 'image': Search engine 'vector_search' validation failed:",
    ):
        spec_validator(
            invalid_spec,
            builder.registered_indexs,
            builder.registered_search_engines,
            builder.registered_aggregators,
        )


@pytest.mark.skip(reason="Aggregator builder/validation not fully implemented yet")
def test_spec_validator_valid_with_aggregator() -> None:
    """Test spec_validator with valid data including an aggregator."""
    # Assuming a valid spec structure with an aggregator
    valid_spec = {
        "index": [
            {
                "name": "description",
                "type": "text_index",
                "search_engine": {"type": "text_search"},
            },
        ],
        "aggregator": {"type": "some_aggregator", "param": "value"},
    }

    try:
        spec_validator(
            valid_spec,
            builder.registered_indexs,
            builder.registered_search_engines,
            builder.registered_aggregators,  # Ensure this includes aggregator types
        )
    except SpecSchemaError as e:
        pytest.fail(f"spec_validator raised an unexpected exception: {e}")


@pytest.mark.skip(reason="Aggregator builder/validation not fully implemented yet")
def test_spec_validator_missing_aggregator_type() -> None:
    """Test spec_validator with a missing aggregator type."""
    invalid_spec = {
        "index": [
            {
                "name": "description",
                "type": "text_index",
                "search_engine": {"type": "text_search"},
            },
        ],
        "aggregator": {
            # "type": "some_aggregator", # Missing type  # noqa: ERA001
            "param": "value",
        },
    }
    with pytest.raises(
        SpecSchemaError,
        match="Spec 'aggregator': Aggregator type is missing.",
    ):
        spec_validator(
            invalid_spec,
            builder.registered_indexs,
            builder.registered_search_engines,
            builder.registered_aggregators,
        )


@pytest.mark.skip(reason="Aggregator builder/validation not fully implemented yet")
def test_spec_validator_unknown_aggregator_type() -> None:
    """Test spec_validator with an unknown aggregator type."""
    invalid_spec = {
        "index": [
            {
                "name": "description",
                "type": "text_index",
                "search_engine": {"type": "text_search"},
            },
        ],
        "aggregator": {"type": "unknown_aggregator", "param": "value"},
    }
    with pytest.raises(
        SpecSchemaError,
        match="Spec 'aggregator': Aggregator type 'unknown_aggregator' is unknown.",
    ):
        spec_validator(
            invalid_spec,
            builder.registered_indexs,
            builder.registered_search_engines,
            builder.registered_aggregators,
        )


@pytest.mark.skip(reason="Aggregator builder/validation not fully implemented yet")
def test_spec_validator_invalid_aggregator_schema() -> None:
    """Test spec_validator with an invalid aggregator schema (Pydantic error)."""
    invalid_spec = {
        "index": [
            {
                "name": "description",
                "type": "text_index",
                "search_engine": {"type": "text_search"},
            },
        ],
        "aggregator": {
            "type": "some_aggregator",
            "required_param": None,  # Assuming this causes validation error
        },
    }
    with pytest.raises(
        SpecSchemaError,
        match="Spec 'aggregator': Aggregator 'some_aggregator' validation failed:",
    ):
        spec_validator(
            invalid_spec,
            builder.registered_indexs,
            builder.registered_search_engines,
            builder.registered_aggregators,
        )
