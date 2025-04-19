"""Registry for Massive Search."""

from collections.abc import Callable
from inspect import signature

from pydantic import BaseModel

from massivesearch.aggregator import BaseAggregator
from massivesearch.index import BaseIndex
from massivesearch.model import BaseAIClient
from massivesearch.pipe.validator import (
    validate_aggregator,
    validate_ai_client,
    validate_search_engine,
)
from massivesearch.search_engine import BaseSearchEngine


class MassiveSearchRegistry:
    """Registry for Massive Search."""

    def __init__(self) -> None:
        """Initialize the registry."""
        self.registered_index_types: dict[str, type[BaseIndex]] = {}
        self.registered_search_engine_types: dict[str, type[BaseSearchEngine]] = {}
        self.registered_aggregator_types: dict[str, type[BaseAggregator]] = {}
        self.registered_ai_client_types: dict[str, type[BaseAIClient]] = {}

    def _get_arguments_type(
        self,
        search_engine: BaseSearchEngine,
    ) -> type[BaseModel]:
        """Get the arguments type for the search engine."""
        if not search_engine:
            msg = "No search engine available to get arguments type."
            raise ValueError(msg)

        search_function = type(search_engine).search
        search_parameters = signature(search_function).parameters
        if "arguments" not in search_parameters:
            msg = "'arguments' parameter not found in search function."
            raise ValueError(msg)
        if not issubclass(
            search_parameters["arguments"].annotation,
            BaseModel,
        ):
            msg = "'arguments' parameter is not a subclass of BaseModel."
            raise TypeError(msg)

        return search_parameters["arguments"].annotation

    def _register_types(
        self,
        component_type_name: str,
        registry: dict[str, type],
        base_class: type,
        name: str,
        cls: type,
    ) -> None:
        """Register a component type with validation."""
        if not name:
            msg = "Name is required."
            raise ValueError(msg)

        if not issubclass(cls, base_class):
            msg = f"Class '{cls.__name__}' is not a subclass of {base_class.__name__}."
            raise TypeError(msg)

        if name in registry:
            msg = f"{component_type_name} with name '{name}' is already registered."
            raise ValueError(msg)
        registry[name] = cls

    def index_type(self, name: str) -> Callable[[type[BaseIndex]], type[BaseIndex]]:
        """Return a decorator to register an index type with a given key name."""
        return lambda cls: self.register_index_type(name, cls)

    def register_index_type(self, name: str, cls: type[BaseIndex]) -> type[BaseIndex]:
        """Register an index type with a given key name."""
        self._register_types(
            "Index",
            self.registered_index_types,
            BaseIndex,
            name,
            cls,
        )
        return cls

    def search_engine_type(
        self,
        name: str,
    ) -> Callable[[type[BaseSearchEngine]], type[BaseSearchEngine]]:
        """Return a decorator to register a search engine type with a given key name."""
        return lambda cls: self.register_search_engine_type(name, cls)

    def register_search_engine_type(
        self,
        name: str,
        cls: type[BaseSearchEngine],
    ) -> type[BaseSearchEngine]:
        """Register a search engine type with a given key name."""
        validate_search_engine(cls)
        self._register_types(
            "Search engine",
            self.registered_search_engine_types,
            BaseSearchEngine,
            name,
            cls,
        )
        return cls

    def aggregator_type(
        self,
        name: str,
    ) -> Callable[[type[BaseAggregator]], type[BaseAggregator]]:
        """Return a decorator to register an aggregator type with a given key name."""
        return lambda cls: self.register_aggregator_type(name, cls)

    def register_aggregator_type(
        self,
        name: str,
        cls: type[BaseAggregator],
    ) -> type[BaseAggregator]:
        """Register an aggregator type with a given key name."""
        validate_aggregator(cls)
        self._register_types(
            "Aggregator",
            self.registered_aggregator_types,
            BaseAggregator,
            name,
            cls,
        )
        return cls

    def ai_client_type(
        self,
        name: str,
    ) -> Callable[[type[BaseAIClient]], type[BaseAIClient]]:
        """Return a decorator to register an AI client type with a given key name."""
        return lambda cls: self.register_ai_client_type(name, cls)

    def register_ai_client_type(
        self,
        name: str,
        cls: type[BaseAIClient],
    ) -> type[BaseAIClient]:
        """Register an AI client type with a given key name."""
        validate_ai_client(cls)
        self._register_types(
            "AI client",
            self.registered_ai_client_types,
            BaseAIClient,
            name,
            cls,
        )
        return cls
