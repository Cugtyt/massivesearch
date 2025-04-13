"""Tests for validating spec files."""

from pathlib import Path

import pytest
import yaml

from supersearch.spec.validator import (
    SpecIndexTypeError,
    SpecSearchEngineError,
    SpecValidationError,
    spec_validator,
)


def test_spec_validator_valid() -> None:
    """Test spec_validator with valid data."""
    with Path("./test/spec/test_spec.yaml").open() as file:
        valid_spec = yaml.safe_load(file)

    try:
        spec_validator(valid_spec)
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
        spec_validator(invalid_spec)

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
        spec_validator(invalid_spec)


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
        spec_validator(invalid_spec)


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
        spec_validator(invalid_spec)
