"""Spec file validator."""

import inspect
import typing

from pydantic import BaseModel, ValidationError

from massivesearch.aggregator.base import BaseAggregator, MassiveSearchTasks
from massivesearch.index.base import BaseIndex
from massivesearch.model.base import BaseAIClient
from massivesearch.pipe.spec_index import MassiveSearchIndex
from massivesearch.search_engine.base import BaseSearchEngine


class SpecSchemaError(Exception):
    """Spec index type errors."""

    def __init__(self, name: str, message: str) -> None:
        """Initialize the exception with name and message."""
        super().__init__(f"Spec '{name}': {message}")


def validate_spec(
    spec: dict,
    registered_indexs: dict[str, type[BaseIndex]],
    registered_search_engines: dict[str, type[BaseSearchEngine]],
    registered_aggregators: dict[str, type[BaseAggregator]],
    registered_ai_clients: dict[str, type[BaseAIClient]],
) -> None:
    """Validate the spec."""
    if not spec:
        name = "spec"
        msg = "No schemas available to build."
        raise SpecSchemaError(name, msg)
    if not isinstance(spec, dict):
        name = "spec"
        msg = "Spec must be a dictionary."
        raise SpecSchemaError(name, msg)

    spec_keys = {"indexs", "aggregator", "ai_client"}
    if set(spec.keys()) != spec_keys:
        name = "spec"
        msg = f"Spec keys must be exactly {spec_keys}, but got {set(spec.keys())}"
        raise SpecSchemaError(name, msg)

    validate_index_spec(
        spec["indexs"],
        registered_indexs,
    )
    validate_search_engine_spec(
        spec["indexs"],
        registered_search_engines,
    )
    validate_aggregator_spec(
        spec["aggregator"],
        registered_aggregators,
    )
    validate_ai_client_spec(
        spec["ai_client"],
        registered_ai_clients,
    )


def validate_index_spec(
    index_spec: list[dict],
    registered_indexs: dict[str, type[BaseIndex]],
) -> None:
    """Validate the index."""
    if not isinstance(index_spec, list):
        name = "indexs"
        msg = "Indexs spec must be a list."
        raise SpecSchemaError(name, msg)
    for index in index_spec:
        if "name" not in index:
            msg = "Index name is missing."
            raise SpecSchemaError(index["name"], msg)
        if "type" not in index:
            msg = "Index type is missing."
            raise SpecSchemaError(index["name"], msg)
        index_name = index["name"]
        index_type = index["type"]
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


def validate_search_engine_spec(
    index_spec: list[dict],
    registered_search_engines: dict[str, type[BaseSearchEngine]],
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
            raise SpecSchemaError(index["name"], msg)
        if "search_engine" not in index:
            msg = f"Index '{index['name']}' search_engine is missing."
            raise SpecSchemaError(index["name"], msg)
        search_engine = index["search_engine"]
        if "type" not in search_engine:
            msg = "Search engine type is missing."
            raise SpecSchemaError(index["name"], msg)
        search_engine_type = search_engine["type"]
        if search_engine_type not in registered_search_engines:
            msg = f"Search engine type '{search_engine_type}' is unknown."
            raise SpecSchemaError(index["name"], msg)

        try:
            search_engine_class = registered_search_engines[search_engine_type]
            search_engine_class(**search_engine)
        except ValidationError as e:
            msg = f"Search engine '{search_engine_type}' validation failed: {e}"
            raise SpecSchemaError(index["name"], msg) from e
        except Exception as e:
            msg = f"Search engine '{search_engine_type}' initialization failed: {e}"
            raise SpecSchemaError(index["name"], msg) from e


def validate_aggregator_spec(
    aggregator_spec: dict,
    registered_aggregators: dict[str, type[BaseAggregator]],
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


def validate_ai_client_spec(
    ai_client_spec: dict,
    registered_ai_clients: dict[str, type[BaseAIClient]],
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
        name = "ai_client"
        msg = f"AI client type '{ai_client_type}' is unknown."
        raise SpecSchemaError(name, msg)

    try:
        ai_client_class = registered_ai_clients[ai_client_type]
        ai_client_class(**ai_client_spec)
    except ValidationError as e:
        name = "ai_client"
        msg = f"AI client '{ai_client_type}' validation failed: {e}"
        raise SpecSchemaError(name, msg) from e
    except Exception as e:
        name = "ai_client"
        msg = f"AI client '{ai_client_type}' initialization failed: {e}"
        raise SpecSchemaError(name, msg) from e


def validate_search_engine(cls: type[BaseSearchEngine]) -> None:
    """Validate the search engine."""
    if hasattr(cls, "search") and not callable(cls.search):
        msg = f"{cls.__name__} must have a callable search method."
        raise AttributeError(msg)
    if not inspect.iscoroutinefunction(cls.search):
        msg = f"{cls.__name__} search method must be async (use 'async def')."
        raise TypeError(msg)
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

    arguments_annotation = cls.search.__annotations__["arguments"]
    if not issubclass(arguments_annotation, BaseModel):
        msg = f"{cls.__name__} search method arguments must be a subclass of BaseModel."
        raise TypeError(msg)
    if cls.search.__annotations__.get("return") is None:
        msg = f"{cls.__name__} search method must have a return type."
        raise AttributeError(msg)


def validate_aggregator(cls: type[BaseAggregator]) -> None:
    """Validate the aggregator."""
    if hasattr(cls, "aggregate") and not callable(cls.aggregate):
        msg = f"{cls.__name__} must have a callable aggregate method."
    if not inspect.iscoroutinefunction(cls.aggregate):
        msg = f"{cls.__name__} aggregate method must be async (use 'async def')."
        raise AttributeError(msg)
    if cls.aggregate.__annotations__.get("tasks") is None:
        msg = f"{cls.__name__} aggregate method must have an tasks attribute."
        raise AttributeError(msg)

    tasks_annotation = cls.aggregate.__annotations__["tasks"]
    origin = typing.get_origin(tasks_annotation)
    args = typing.get_args(tasks_annotation)

    if origin is not MassiveSearchTasks:
        msg = (
            f"{cls.__name__} aggregate 'tasks' annotation must be "
            f"MassiveSearchTasks[BaseSearchResultIndex]."
        )
        raise TypeError(msg)

    if args is None or len(args) != 1:
        msg = (
            f"{cls.__name__} aggregate 'tasks' annotation must be "
            f"MassiveSearchTasks[BaseSearchResultIndex]."
        )
        raise TypeError(msg)

    aggregate_parameters = cls.aggregate.__code__.co_varnames[
        : cls.aggregate.__code__.co_argcount
    ]
    if aggregate_parameters != ("self", "tasks"):
        msg = (
            f"{cls.__name__} aggregate method must only have 'self' and "
            f"'tasks' as parameters."
        )
        raise TypeError(msg)

    if getattr(cls.aggregate, "__isabstractmethod__", False):
        msg = f"{cls.__name__} aggregate method must not be abstract."
        raise TypeError(msg)


def validate_ai_client(cls: type[BaseAIClient]) -> None:
    """Validate the AI client."""
    if hasattr(cls, "response") and not callable(cls.response):
        msg = f"{cls.__name__} must have a callable response method."
        raise AttributeError(msg)
    if not inspect.iscoroutinefunction(cls.response):
        msg = f"{cls.__name__} response method must be async (use 'async def')."
        raise TypeError(msg)
    if cls.response.__annotations__.get("messages") is None:
        msg = f"{cls.__name__} response method must have a messages attribute."
        raise AttributeError(msg)

    response_parameters = cls.response.__code__.co_varnames[
        : cls.response.__code__.co_argcount
    ]
    if response_parameters != ("self", "messages", "format_model"):
        msg = (
            f"{cls.__name__} response method must only have 'self', "
            f"'messages' and 'format_model' as parameters."
        )
        raise TypeError(msg)

    if getattr(cls.response, "__isabstractmethod__", False):
        msg = f"{cls.__name__} response method must not be abstract."
        raise TypeError(msg)


def validate_pipe_search_result_index(
    indexs: list[MassiveSearchIndex],
    aggregator: BaseAggregator,
    pipe_return_type: type,
) -> None:
    """Validate the search result index."""
    if not isinstance(indexs, list):
        msg = "Indexs must be a list."
        raise TypeError(msg)
    if not isinstance(aggregator, BaseAggregator):
        msg = "Aggregator must be a BaseAggregator."
        raise TypeError(msg)

    for index in indexs:
        if not isinstance(index, MassiveSearchIndex):
            msg = "Index must be a MassiveSearchIndex."
            raise TypeError(msg)

    search_return_type = indexs[0].search_engine.search.__annotations__["return"]
    for index in indexs:
        return_type = index.search_engine.search.__annotations__["return"]
        if return_type is not search_return_type:
            msg = (
                f"Search return type of {index.name} is mismatched."
                f" Found two different search return types:"
                f" {return_type} and {search_return_type}."
                f" Please check the indexs."
            )
            raise TypeError(msg)

    aggregator_tasks_annotation = aggregator.aggregate.__annotations__["tasks"]
    args = typing.get_args(aggregator_tasks_annotation)

    if args[0] is not search_return_type:
        msg = (
            "Aggregator 'tasks' annotation does not match the search "
            f"return type."
            f" Expected {search_return_type}, got {args[0]}."
            f" Please check the aggregator and indexs."
        )
        raise TypeError(msg)

    aggregator_sig = inspect.signature(aggregator.aggregate)
    aggregator_return_type = aggregator_sig.return_annotation
    if typing.get_origin(aggregator_return_type) is typing.Awaitable:
        aggregator_return_type = typing.get_args(aggregator_return_type)[0]

    if aggregator_return_type is not pipe_return_type:
        msg = (
            "Aggregator return type does not match the pipe return type."
            f" Expected {pipe_return_type}, got {aggregator_return_type}."
            f" Please check the aggregator and pipe return type."
        )
        raise TypeError(msg)
