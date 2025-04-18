"""Pipe."""

import asyncio
from collections.abc import Callable
from inspect import signature
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field, ValidationError, create_model

from massivesearch.aggregator.base import (
    BaseAggregator,
    BaseAggregatorResult,
    MassiveSearchTasks,
)
from massivesearch.index.base import BaseIndex
from massivesearch.model.base import BaseAIClient
from massivesearch.pipe.prompt import PIPE_STSTEM_PROMPT_TEMPLATE
from massivesearch.pipe.spec_index import MassiveSearchIndex
from massivesearch.pipe.validator import (
    validate_aggregator,
    validate_ai_client,
    validate_pipe_search_result_index,
    validate_search_engine,
    validate_spec,
)
from massivesearch.search_engine.base import (
    BaseSearchEngine,
    BaseSearchEngineArguments,
)


class MassiveSearchPipe:
    """Massive Search Pipe."""

    def __init__(self, *, prompt_template: str | None = None) -> None:
        """Initialize the Massive Search Pipe."""
        self.indexs: list[MassiveSearchIndex] = []
        self.aggregator: BaseAggregator | None = None
        self.ai_client: BaseAIClient | None = None

        self.registered_index_types: dict[str, type[BaseIndex]] = {}
        self.registered_search_engine_types: dict[str, type[BaseSearchEngine]] = {}
        self.registered_aggregator_types: dict[str, type[BaseAggregator]] = {}
        self.registered_ai_client_types: dict[str, type[BaseAIClient]] = {}

        if prompt_template and "{context}" not in prompt_template:
            msg = "Prompt template must contain '{context}' placeholder."
            raise ValueError(msg)
        self.prompt_template = prompt_template or PIPE_STSTEM_PROMPT_TEMPLATE

        self.prompt: str = ""
        self.format_model: type[BaseModel] | None = None
        self.serach_query: list[dict] = []

    def build_from_file(self, file_path: str) -> None:
        """Build the spec from a path."""
        if not file_path:
            msg = "File path is required."
            raise ValueError(msg)
        if not Path(file_path).exists():
            msg = f"File path '{file_path}' does not exist."
            raise FileNotFoundError(msg)
        if not Path(file_path).is_file():
            msg = f"File path '{file_path}' is not a file."
            raise ValueError(msg)
        if not file_path.endswith(".yaml") and not file_path.endswith(".yml"):
            msg = f"File path '{file_path}' is not a YAML file."
            raise ValueError(msg)

        with Path(file_path).open() as file:
            spec = yaml.safe_load(file)
        self.build(spec)

    def build(self, spec: dict) -> None:
        """Build the spec."""
        if not spec:
            msg = "No schemas available to build."
            raise ValueError(msg)

        validate_spec(
            spec,
            self.registered_index_types,
            self.registered_search_engine_types,
            self.registered_aggregator_types,
            self.registered_ai_client_types,
        )

        indexs_spec = spec["indexs"]
        for index_spec in indexs_spec:
            name = index_spec.get("name")
            index_type = index_spec.get("type")
            search_engine_spec = index_spec.get("search_engine")
            search_engine_type = search_engine_spec.get("type")
            index = self.registered_index_types[index_type](**index_spec)
            search_engine = self.registered_search_engine_types[search_engine_type](
                **search_engine_spec,
            )
            self.indexs.append(
                MassiveSearchIndex(
                    name=name,
                    index=index,
                    search_engine=search_engine,
                    search_engine_arguments_type=self._get_arguments_type(
                        search_engine,
                    ),
                ),
            )

        aggregator_spec = spec["aggregator"]
        aggregator_type = aggregator_spec["type"]
        self.aggregator = self.registered_aggregator_types[aggregator_type](
            **aggregator_spec,
        )

        ai_client_spec = spec["ai_client"]
        ai_client_type = ai_client_spec["type"]
        self.ai_client = self.registered_ai_client_types[ai_client_type](
            **ai_client_spec,
        )

        validate_pipe_search_result_index(self.indexs, self.aggregator)

        self._build_prompt()
        self._build_format_model()

    def _build_prompt(self) -> None:
        """Build the prompt for the spec."""
        if not self.indexs or not self.aggregator or not self.ai_client:
            msg = "Spec is not fully built. Cannot build prompt."
            raise ValueError(msg)

        context = "\n".join(index.prompt() for index in self.indexs)
        self.prompt = self.prompt_template.format(context=context)

    def _build_format_model(self) -> None:
        """Build the format model for the spec."""
        if not self.indexs or not self.aggregator or not self.ai_client:
            msg = "Spec is not fully built. Cannot build format model."
            raise ValueError(msg)

        fields: dict[str, Any] = {"sub_query": (str, ...)}
        for index in self.indexs:
            arg_type: type[BaseSearchEngineArguments] = (
                index.search_engine_arguments_type
            )
            fields[index.name] = (arg_type, ...)

        SingleQueryFormat: type[BaseModel] = create_model(  # noqa: N806
            "SingleQueryFormat",
            **fields,
            __base__=BaseModel,
        )

        self.format_model = create_model(
            "MultiQueryFormat",
            queries=(list[SingleQueryFormat], Field(...)),  # type: ignore[valid-type]
            __base__=BaseModel,
        )

    def _get_arguments_type(
        self,
        search_engine: BaseSearchEngine,
    ) -> type[BaseSearchEngineArguments]:
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
            BaseSearchEngineArguments,
        ):
            msg = (
                "'arguments' parameter is not a subclass of BaseSearchEngineArguments."
            )
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

    def __or__(self, other: "MassiveSearchPipe") -> "MassiveSearchPipe":
        """Combine two MassiveSearchPipe instances."""
        if not isinstance(other, MassiveSearchPipe):
            msg = "Can only combine with another MassiveSearchPipe instance."
            raise TypeError(msg)

        if self.aggregator or other.aggregator:
            msg = "Aggregator already set in one or both pipes. Cannot combine."
            raise ValueError(msg)

        if self.ai_client or other.ai_client:
            msg = "AI client already set in one or both pipes. Cannot combine."
            raise ValueError(msg)

        type_registries_to_check: list[tuple[dict[str, type], dict[str, type], str]] = [
            (self.registered_index_types, other.registered_index_types, "Index types"),
            (
                self.registered_search_engine_types,
                other.registered_search_engine_types,
                "Search engine types",
            ),
            (
                self.registered_aggregator_types,
                other.registered_aggregator_types,
                "Aggregator types",
            ),
            (
                self.registered_ai_client_types,
                other.registered_ai_client_types,
                "AI client types",
            ),
        ]

        for self_registry, other_registry, type_name in type_registries_to_check:
            overlap = set(self_registry) & set(other_registry)
            if overlap:
                msg = (
                    f"{type_name} overlap: {overlap}. "
                    "Cannot combine pipes with duplicate type names."
                )
                raise ValueError(msg)

        combined = MassiveSearchPipe()
        combined.registered_index_types = {
            **self.registered_index_types,
            **other.registered_index_types,
        }
        combined.registered_search_engine_types = {
            **self.registered_search_engine_types,
            **other.registered_search_engine_types,
        }
        combined.registered_aggregator_types = {
            **self.registered_aggregator_types,
            **other.registered_aggregator_types,
        }
        combined.registered_ai_client_types = {
            **self.registered_ai_client_types,
            **other.registered_ai_client_types,
        }
        return combined

    def _build_messages(self, query: str) -> list[dict[str, str]]:
        """Build the prompt for the spec."""
        return [
            {
                "role": "system",
                "content": self.prompt,
            },
            {
                "role": "user",
                "content": query,
            },
        ]

    async def build_query(self, query: str) -> list[dict]:
        """Generate the query based on the spec."""
        if not self.ai_client:
            msg = "AI client is not set. Cannot build query."
            raise ValueError(msg)
        if not self.format_model:
            msg = "Format model is not set. Cannot build query."
            raise ValueError(msg)
        try:
            response = await self.ai_client.response(
                self._build_messages(query),
                self.format_model,
            )
            self.format_model(**response)
            self.serach_query = response["queries"]
            return response["queries"]
        except KeyError:
            msg = "Failed to parse response: 'queries' key not found."
            raise ValueError(msg) from None
        except ValidationError as e:
            msg = f"Model didn't respond with a valid query: {e}"
            raise ValueError(msg) from e
        except Exception as e:
            msg = f"Unexpected error: {e}"
            raise ValueError(msg) from e

    async def search_task(self, query: str) -> MassiveSearchTasks:
        """Search for the query."""
        search_queries = await self.build_query(query)
        search_tasks: MassiveSearchTasks = []
        for search_query in search_queries:
            result = {}
            for index in self.indexs:
                search_engine_arguments = index.search_engine_arguments_type(
                    **search_query[index.name],
                )
                search_result = asyncio.create_task(
                    index.search_engine.search(
                        search_engine_arguments,
                    ),
                )
                result[index.name] = search_result
            search_tasks.append(result)

        return search_tasks

    async def run(self, query: str) -> BaseAggregatorResult:
        """Execute the query and return the aggregated result."""
        if not self.aggregator:
            msg = "Aggregator is not set. Cannot run query."
            raise ValueError(msg)
        return await self.aggregator.aggregate(await self.search_task(query))
