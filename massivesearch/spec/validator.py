"""Spec file validator."""

from pydantic import ValidationError

from massivesearch.spec.base_index import BaseIndex
from massivesearch.spec.base_search_engine import (
    BaseSearchEngine,
    BaseSearchEngineArguments,
    BaseSearchEngineConfig,
    BaseSearchResultIndex,
)


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


def spec_validator(
    spec: dict,
    registered_indexs: dict[str, BaseIndex],
    registered_search_engines: dict[str, BaseSearchEngine],
) -> None:
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


def validate_search_engine(cls: type[BaseSearchEngine]) -> None:
    """Validate the search engine class."""
    _validate_config(cls)
    _validate_search_method(cls)


def _validate_config(cls: type[BaseSearchEngine]) -> None:
    if cls.model_fields.get("config") is None:
        msg = f"{cls.__name__} must have a config attribute."
        raise AttributeError(msg)
    if not issubclass(
        cls.model_fields.get("config").annotation,
        BaseSearchEngineConfig,
    ):
        msg = f"{cls.__name__} config must be a subclass of BaseSearchEngineConfig."
        raise TypeError(msg)


def _validate_search_method(cls: type[BaseSearchEngine]) -> None:
    if hasattr(cls, "search") and not callable(cls.search):
        msg = f"{cls.__name__} must have a callable search method."
        raise AttributeError(msg)
    if cls.search.__annotations__.get("arguments") is None:
        msg = f"{cls.__name__} search method must have an arguments attribute."
        raise AttributeError(msg)
    arguments_annotation = cls.search.__annotations__.get("arguments")
    if not issubclass(arguments_annotation, BaseSearchEngineArguments):
        msg = (
            f"{cls.__name__} search method arguments must be a "
            f"subclass of BaseSearchEngineArguments."
        )
        raise TypeError(msg)
    if cls.search.__annotations__.get("return") is None:
        msg = f"{cls.__name__} search method must have a return type."
        raise AttributeError(msg)
    return_annotation = cls.search.__annotations__.get("return")
    if not issubclass(return_annotation, BaseSearchResultIndex):
        msg = (
            f"{cls.__name__} search method return type must be a "
            f"subclass of BaseSearchResult."
        )
        raise TypeError(msg)
