"""Spec file validator."""

from pydantic import ValidationError

from supersearch.index import registered_schemas
from supersearch.search_engine import registered_search_engines


class SpecIndexTypeError(Exception):
    """Spec index type errors."""

    def __init__(self, index_name: str, type_name: str) -> None:
        """Initialize the exception with a type name."""
        super().__init__(
            f"Index '{index_name}' schema with type name '{type_name}' is unknown.",
        )


class SpecSearchEngineError(Exception):
    """Spec index type errors."""

    def __init__(self, index_name: str, type_name: str) -> None:
        """Initialize the exception with a type name."""
        super().__init__(
            (
                f"Index '{index_name}' schema with search engine type name "
                f"'{type_name}' is unknown."
            ),
        )


class SpecValidationError(Exception):
    """Custom exception for spec validation errors."""

    def __init__(self, errors: dict) -> None:
        """Initialize the exception with index and search engine type and errors."""
        super().__init__(
            f"Spec validation errors: {errors}",
        )


def spec_validator(spec: dict) -> None:
    """Validate the spec."""
    validation_errors = {}
    for index_name, schema in spec.items():
        index_type_name = schema.get("type")
        if index_type_name not in registered_schemas:
            raise SpecIndexTypeError(index_name, index_type_name)
        search_engine_type_name: str = schema.get("search_engine", {}).get("type", "")
        if search_engine_type_name not in registered_search_engines:
            raise SpecSearchEngineError(index_name, search_engine_type_name)
        try:
            registered_schemas[index_type_name](**schema)
            registered_search_engines[search_engine_type_name].model_fields[
                "config"
            ].annotation(**schema.get("search_engine"))
        except ValidationError as e:
            validation_errors[index_name] = str(e)

    if validation_errors:
        raise SpecValidationError(validation_errors)
