"""Tests for validating index file schemas."""

from pathlib import Path

import pytest
import yaml

from supersearch.index import (
    SchemaTypeError,
    SchemaValidationError,
    index_validator,
)


def test_yaml_validator_valid() -> None:
    """Test yaml_validator with valid data."""
    with Path("./test/schema/test_index.yaml").open() as file:
        yaml_data = yaml.safe_load(file)

    try:
        index_validator(yaml_data)
    except SchemaTypeError as e:
        pytest.fail(f"yaml_validator raised a SchemaTypeError: {e}")
    except SchemaValidationError as e:
        pytest.fail(f"yaml_validator raised a SchemaValidationError: {e}")


def test_yaml_validator_invalid_type() -> None:
    """Test yaml_validator with an invalid type."""
    invalid_yaml = {
        "unknown_type": {
            "type": "unknown",
            "description": "An unknown type.",
        },
    }

    with pytest.raises(SchemaTypeError) as excinfo:
        index_validator(invalid_yaml)

    if "Index 'unknown_type' schema with type name 'unknown'" not in str(excinfo.value):
        msg = (
            "Expected 'Index 'unknown_type' schema with type name 'unknown''"
            " in exception message."
        )
        raise AssertionError(msg)


def test_yaml_validator_invalid_schema() -> None:
    """Test yaml_validator with an invalid schema."""
    invalid_yaml = {
        "price": {
            "type": "number",
            "description": "The price of the product.",
            "range": {
                "min": "invalid",
                "max": 10000,
            },
            "examples": [19.99, 999.99, 0.00],
        },
    }

    with pytest.raises(SchemaValidationError) as excinfo:
        index_validator(invalid_yaml)
    if "validation errors" not in str(excinfo.value):
        msg = "Expected 'validation errors' in exception message."
        raise AssertionError(msg)
