"""Spec file validator."""

from pydantic import ValidationError

from supersearch.index import registered_indexs
from supersearch.search_engine import registered_search_engines


class SpecIndexTypeError(Exception):
    """Spec index type errors."""

    def __init__(self, name: str, message: str) -> None:
        """Initialize the exception with name and message."""
        super().__init__(f"Spec '{name}': {message}")


class SpecSearchEngineError(Exception):
    """Spec search engine type errors."""

    def __init__(self, name: str, message: str) -> None:
        """Initialize the exception with name and message."""
        super().__init__(f"Spec '{name}': {message}")


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
    for name, schema in spec.items():
        index_schema = schema.get("index")

        if index_schema is None:
            msg = f"Index schema for '{name}' is missing."
            raise SpecIndexTypeError(name, msg)

        search_engine_schema = schema.get("search_engine")

        if search_engine_schema is None:
            msg = f"Search engine schema for '{name}' is missing."
            raise SpecSearchEngineError(name, msg)

        if index_schema.get("type") not in registered_indexs:
            msg = f"Index type '{index_schema.get('type')}' is unknown."
            raise SpecIndexTypeError(name, msg)

        if search_engine_schema.get("type") not in registered_search_engines:
            msg = f"Search engine type '{search_engine_schema.get('type')}' is unknown."
            raise SpecSearchEngineError(name, msg)

        try:
            registered_indexs[index_schema.get("type")](**index_schema)
            if search_engine_schema.get("config") is None:
                search_engine_schema["config"] = {}
            registered_search_engines[search_engine_schema.get("type")](
                **search_engine_schema,
            )
        except ValidationError as e:
            validation_errors[name] = str(e)

    if validation_errors:
        raise SpecValidationError(validation_errors)
