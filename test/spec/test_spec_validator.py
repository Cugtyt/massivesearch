"""Tests for validating spec files."""

from pathlib import Path

import pytest
import yaml

from supersearch.index import (
    bool_index_spec_builder,
    date_index_spec_builder,
    number_index_spec_builder,
    text_index_spec_builder,
    vector_index_spec_builder,
)
from supersearch.search_engine import (
    bool_search_engine_spec_builder,
    date_search_engine_spec_builder,
    number_search_engine_spec_builder,
    text_search_engine_spec_builder,
    vector_search_engine_spec_builder,
)
from supersearch.spec import (
    SpecIndexTypeError,
    SpecSearchEngineError,
    SpecValidationError,
    spec_validator,
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
        )
    except (SpecIndexTypeError, SpecSearchEngineError, SpecValidationError) as e:
        pytest.fail(f"spec_validator raised an unexpected exception: {e}")


def test_spec_validator_invalid_index_type() -> None:
    """Test spec_validator with an invalid index type."""
    invalid_spec = {
        "unknown": {
            "search_engine": {
                "type": "text_search",
            },
        },
    }

    with pytest.raises(SpecIndexTypeError):
        spec_validator(
            invalid_spec,
            builder.registered_indexs,
            builder.registered_search_engines,
        )

    invalid_spec = {
        "unknow": {
            "index": {
                "type": "unknown",
                "description": "An unknown index type.",
            },
            "search_engine": {
                "type": "text_search",
            },
        },
    }
    with pytest.raises(
        SpecIndexTypeError,
        match="Spec 'unknow': Index type 'unknown' is unknown.",
    ):
        spec_validator(
            invalid_spec,
            builder.registered_indexs,
            builder.registered_search_engines,
        )


def test_spec_validator_invalid_search_engine_type() -> None:
    """Test spec_validator with an invalid search engine type."""
    invalid_spec = {
        "description": {
            "index": {
                "type": "text_index",
                "description": "A detailed description of the product.",
            },
            "search_engine": {
                "type": "unknown_engine",
            },
        },
    }

    with pytest.raises(
        SpecSearchEngineError,
        match="Spec 'description': Search engine type 'unknown_engine' is unknown.",
    ):
        spec_validator(
            invalid_spec,
            builder.registered_indexs,
            builder.registered_search_engines,
        )


def test_spec_validator_invalid_schema() -> None:
    """Test spec_validator with an invalid schema."""
    invalid_spec = {
        "price": {
            "index": {
                "type": "number_index",
                "description": "The price of the product.",
                "range": {
                    "min": 0,
                    "max": 10000,
                },
            },
            "search_engine": {
                "type": "number_search",
            },
        },
    }

    with pytest.raises(SpecValidationError, match="Spec validation errors:"):
        spec_validator(
            invalid_spec,
            builder.registered_indexs,
            builder.registered_search_engines,
        )
