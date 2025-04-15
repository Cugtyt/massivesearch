"""Spec file validator."""

from pydantic import ValidationError

from massivesearch.aggregator.base import BaseAggregator
from massivesearch.index.base import BaseIndex
from massivesearch.search_engine.base import (
    BaseSearchEngine,
    BaseSearchEngineArguments,
    BaseSearchResultIndex,
)


class SpecSchemaError(Exception):
    """Spec index type errors."""

    def __init__(self, name: str, message: str) -> None:
        """Initialize the exception with name and message."""
        super().__init__(f"Spec '{name}': {message}")


def spec_validator(
    spec: dict,
    registered_indexs: dict[str, BaseIndex],
    registered_search_engines: dict[str, BaseSearchEngine],
    registered_aggregators: dict[str, BaseAggregator],
) -> None:
    """Validate the spec."""
    index_spec = spec.get("indexs")
    if index_spec is None:
        name = "indexs"
        msg = "Indexs spec is missing."
        raise SpecSchemaError(name, msg)
    if not isinstance(index_spec, list):
        name = "indexs"
        msg = "Indexs spec must be a list."
        raise SpecSchemaError(name, msg)

    index_spec_validator(
        index_spec,
        registered_indexs,
    )
    search_engine_spec_validator(
        index_spec,
        registered_search_engines,
    )

    aggregator_spec = spec.get("aggregator")
    if aggregator_spec is None:
        name = "aggregator"
        msg = "Aggregator spec is missing."
        raise SpecSchemaError(name, msg)
    aggregator_spec_validator(
        aggregator_spec,
        registered_aggregators,
    )


def index_spec_validator(
    index_spec: list[dict],
    registered_indexs: dict[str, BaseIndex],
) -> None:
    """Validate the index."""
    for index in index_spec:
        if "name" not in index:
            msg = "Index name is missing."
            raise SpecSchemaError(index.get("name"), msg)
        if "type" not in index:
            msg = "Index type is missing."
            raise SpecSchemaError(index.get("name"), msg)
        index_name = index.get("name")
        index_type = index.get("type")
        if index_type not in registered_indexs:
            msg = f"Index type '{index_type}' is unknown."
            raise SpecSchemaError(index_name, msg)

        try:
            index_class = registered_indexs[index_type]
            index_class(**index)
        except ValidationError as e:
            msg = f"Index '{index_name}' validation failed for '{index_type}': {e}"
            raise SpecSchemaError(index_name, msg) from e
        except Exception as e:
            msg = f"Index '{index_name}' initialization failed for '{index_type}': {e}"
            raise SpecSchemaError(index_name, msg) from e


def search_engine_spec_validator(
    index_spec: list[dict],
    registered_search_engines: dict[str, BaseSearchEngine],
) -> None:
    """Validate the search engine."""
    for index in index_spec:
        if "name" not in index:
            msg = "Index name is missing."
            raise SpecSchemaError(index.get("name"), msg)
        if "search_engine" not in index:
            msg = f"Index '{index.get('name')}' search_engine is missing."
            raise SpecSchemaError(index.get("name"), msg)
        search_engine = index.get("search_engine")
        if "type" not in search_engine:
            msg = "Search engine type is missing."
            raise SpecSchemaError(index.get("name"), msg)
        search_engine_type = search_engine.get("type")
        if search_engine_type not in registered_search_engines:
            msg = f"Search engine type '{search_engine_type}' is unknown."
            raise SpecSchemaError(index.get("name"), msg)

        try:
            search_engine_class = registered_search_engines[search_engine_type]
            search_engine_class(**search_engine)
        except ValidationError as e:
            msg = f"Search engine '{search_engine_type}' validation failed: {e}"
            raise SpecSchemaError(index.get("name"), msg) from e
        except Exception as e:
            msg = f"Search engine '{search_engine_type}' initialization failed: {e}"
            raise SpecSchemaError(index.get("name"), msg) from e


def aggregator_spec_validator(
    aggregator_spec: dict,
    registered_aggregators: dict[str, BaseAggregator],
) -> None:
    """Validate the aggregator."""
    if "type" not in aggregator_spec:
        name = "aggregator"
        msg = "Aggregator type is missing."
        raise SpecSchemaError(name, msg)

    aggregator_type = aggregator_spec.get("type")
    if aggregator_type not in registered_aggregators:
        name = "aggregator"
        msg = f"Aggregator type '{aggregator_type}' is unknown."
        raise SpecSchemaError(name, msg)

    try:
        aggregator_class = registered_aggregators[aggregator_type]
        aggregator_class(**aggregator_spec)
    except ValidationError as e:
        msg = f"Aggregator '{aggregator_type}' validation failed: {e}"
        raise SpecSchemaError(name, msg) from e
    except Exception as e:
        msg = f"Aggregator '{aggregator_type}' initialization failed: {e}"
        raise SpecSchemaError(name, msg) from e


def validate_search_engine(cls: type[BaseSearchEngine]) -> None:
    """Validate the search engine."""
    if hasattr(cls, "search") and not callable(cls.search):
        msg = f"{cls.__name__} must have a callable search method."
        raise AttributeError(msg)
    if cls.search.__annotations__.get("arguments") is None:
        msg = f"{cls.__name__} search method must have an arguments attribute."
        raise AttributeError(msg)

    if getattr(cls.search, "__isabstractmethod__", False):
        msg = f"{cls.__name__} search method must not be abstract."
        raise TypeError(msg)

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
