"""Spec file validator."""

from pydantic import ValidationError

from massivesearch.aggregator.base import BaseAggregator
from massivesearch.index.base import BaseIndex
from massivesearch.model.base import BaseAIClient
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
    registered_ai_clients: dict[str, BaseAIClient],
) -> None:
    """Validate the spec."""
    valid_keys = {"indexs", "aggregator", "ai_client"}
    if spec.keys() - valid_keys:
        name = "spec"
        msg = "Spec contains invalid keys."
        raise SpecSchemaError(name, msg)

    if spec.get("indexs"):
        index_spec_validator(
            spec.get("indexs"),
            registered_indexs,
        )
        search_engine_spec_validator(
            spec.get("indexs"),
            registered_search_engines,
        )
    if spec.get("aggregator"):
        aggregator_spec_validator(
            spec.get("aggregator"),
            registered_aggregators,
        )
    if spec.get("ai_client"):
        ai_client_spec_validator(
            spec.get("ai_client"),
            registered_ai_clients,
        )


def index_spec_validator(
    index_spec: list[dict],
    registered_indexs: dict[str, BaseIndex],
) -> None:
    """Validate the index."""
    if not isinstance(index_spec, list):
        name = "indexs"
        msg = "Indexs spec must be a list."
        raise SpecSchemaError(name, msg)
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
    if not index_spec or not isinstance(index_spec, list):
        name = "indexs"
        msg = "Indexs spec is missing or not a list."
        raise SpecSchemaError(name, msg)
    if not all("search_engine" in index for index in index_spec):
        name = "indexs"
        msg = "Search engine spec is missing in indexs."
        raise SpecSchemaError(name, msg)

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
    if aggregator_spec is None:
        name = "aggregator"
        msg = "Aggregator spec is missing."
        raise SpecSchemaError(name, msg)

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
        name = "aggregator"
        msg = f"Aggregator '{aggregator_type}' validation failed: {e}"
        raise SpecSchemaError(name, msg) from e
    except Exception as e:
        name = "aggregator"
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

    search_parameters = cls.search.__code__.co_varnames[
        : cls.search.__code__.co_argcount
    ]
    if search_parameters != ("self", "arguments"):
        msg = (
            f"{cls.__name__} search method must only have 'self' and "
            f"'arguments' as parameters."
        )
        raise TypeError(msg)

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


def ai_client_spec_validator(
    ai_client_spec: dict,
    registered_ai_clients: dict[str, BaseAIClient],
) -> None:
    """Validate the AI client."""
    if not ai_client_spec or not isinstance(ai_client_spec, dict):
        name = "ai_client"
        msg = "AI client spec is missing or not a dictionary."
        raise SpecSchemaError(name, msg)
    if "type" not in ai_client_spec:
        name = "ai_client"
        msg = "AI client type is missing."
        raise SpecSchemaError(name, msg)
    ai_client_type = ai_client_spec.get("type")
    if ai_client_type not in registered_ai_clients:
        msg = f"AI client type '{ai_client_type}' is unknown."
        raise SpecSchemaError(name, msg)

    try:
        ai_client_class = registered_ai_clients[ai_client_type]
        ai_client_class(**ai_client_spec)
    except ValidationError as e:
        msg = f"AI client '{ai_client_type}' validation failed: {e}"
        raise SpecSchemaError(name, msg) from e
    except Exception as e:
        msg = f"AI client '{ai_client_type}' initialization failed: {e}"
        raise SpecSchemaError(name, msg) from e
