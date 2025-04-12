"""Tests for validating spec files."""

from pathlib import Path

import pytest
import yaml

from supersearch.spec.spec_validator import (
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
        "unknown_index": {
            "type": "unknown",
            "description": "An unknown index type.",
        },
    }

    with pytest.raises(SpecIndexTypeError) as excinfo:
        spec_validator(invalid_spec)

    if "Index 'unknown_index' schema with type name 'unknown'" not in str(
        excinfo.value,
    ):
        msg = "Expected error message not found in exception."
        raise AssertionError(msg)


def test_spec_validator_invalid_search_engine_type() -> None:
    """Test spec_validator with an invalid search engine type."""
    invalid_spec = {
        "description": {
            "type": "text",
            "description": "A detailed description of the product.",
            "search_engine": {
                "type": "unknown_engine",
            },
        },
    }

    with pytest.raises(SpecSearchEngineError) as excinfo:
        spec_validator(invalid_spec)

    if (
        "Index 'description' schema with search engine type name 'unknown_engine'"
        not in str(excinfo.value)
    ):
        msg = (
            "Expected error message not found in exception for invalid search "
            "engine type."
        )
        raise AssertionError(msg)


def test_spec_validator_invalid_schema() -> None:
    """Test spec_validator with an invalid schema."""
    invalid_spec = {
        "price": {
            "type": "number",
            "description": "The price of the product.",
            "range": {
                "min": "invalid",
                "max": 10000,
            },
            "examples": [19.99, 999.99, 0.00],
            "search_engine": {
                "type": "text",
            },
        },
    }

    with pytest.raises(SpecValidationError) as excinfo:
        spec_validator(invalid_spec)

    if "Spec validation errors" not in str(excinfo.value):
        msg = "Expected 'Spec validation errors' in exception message."
        raise AssertionError(msg)
