"""Pipe."""

from inspect import signature
from pathlib import Path

import yaml
from pydantic import BaseModel, ValidationError, create_model

from massivesearch.aggregator.base import BaseAggregator, BaseAggregatorResult
from massivesearch.index.base import BaseIndex
from massivesearch.model.base import BaseAIClient
from massivesearch.pipe.prompt import PIPE_STSTEM_PROMPT_TEMPLATE
from massivesearch.pipe.spec_index import SpecIndex
from massivesearch.pipe.validator import spec_validator
from massivesearch.search_engine.base import BaseSearchEngine, BaseSearchResultIndex

SearchResult = list[dict[str, BaseSearchResultIndex]]


class MassiveSearchPipe:
    """Massive Search Pipe."""

    def __init__(self, *, prompt_template: str | None = None) -> None:
        """Initialize the Massive Search Pipe."""
        self.indexs: list[SpecIndex] = []
        self.aggregator: BaseAggregator = None
        self.ai_client: BaseAIClient = None

        self.registered_index_types: dict[str, type[BaseIndex]] = {}
        self.registered_search_engine_types: dict[str, type[BaseSearchEngine]] = {}
        self.registered_aggregator_types: dict[str, type[BaseAggregator]] = {}
        self.registered_ai_client_types: dict[str, type[BaseAIClient]] = {}

        if prompt_template and "{context}" not in prompt_template:
            msg = "Prompt template must contain '{context}' placeholder."
            raise ValueError(msg)
        self.prompt_template = prompt_template or PIPE_STSTEM_PROMPT_TEMPLATE

        self.prompt: str = ""
        self.format_model: type[BaseModel] = None
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

        spec_validator(
            spec,
            self.registered_index_types,
            self.registered_search_engine_types,
            self.registered_aggregator_types,
            self.registered_ai_client_types,
        )

        indexs_spec = spec.get("indexs")
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
                SpecIndex(
                    name=name,
                    index=index,
                    search_engine=search_engine,
                    search_engine_arguments_type=self._get_arguments_type(
                        search_engine,
                    ),
                ),
            )

        aggregator_spec = spec.get("aggregator")
        aggregator_type = aggregator_spec.get("type")
        self.aggregator = self.registered_aggregator_types[aggregator_type](
            **aggregator_spec,
        )

        ai_client_spec = spec.get("ai_client")
        ai_client_type = ai_client_spec.get("type")
        self.ai_client = self.registered_ai_client_types[ai_client_type](
            **ai_client_spec,
        )

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

        fields = {"sub_query": str}
        for index in self.indexs:
            fields[index.name] = (index.search_engine_arguments_type, ...)

        single_query_format = create_model("SingleQueryFormat", **fields)
        self.format_model = create_model(
            "MultiQueryFormat",
            queries=list[single_query_format],
        )

    def _get_arguments_type(self, search_engine: BaseSearchEngine) -> type[BaseModel]:
        """Get the arguments type for the search engine."""
        if not search_engine:
            msg = "No search engine available to get arguments type."
            raise ValueError(msg)

        search_function = type(search_engine).search
        search_parameters = signature(search_function).parameters
        if "arguments" not in search_parameters:
            msg = "'arguments' parameter not found in search function."
            raise ValueError(msg)
        if not search_parameters["arguments"].annotation:
            msg = "'arguments' parameter has no annotation."
            raise ValueError(msg)

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

    def index_type(self, name: str) -> type[BaseIndex]:
        """Return a decorator to register an index type with a given key name."""
        return lambda cls: self.register_index_type(name, cls)

    def register_index_type(self, name: str, cls: type[BaseIndex]) -> None:
        """Register an index type with a given key name."""
        self._register_types(
            "Index",
            self.registered_index_types,
            BaseIndex,
            name,
            cls,
        )

    def search_engine_type(self, name: str) -> type[BaseSearchEngine]:
        """Return a decorator to register a search engine type with a given key name."""
        return lambda cls: self.register_search_engine_type(name, cls)

    def register_search_engine_type(
        self,
        name: str,
        cls: type[BaseSearchEngine],
    ) -> None:
        """Register a search engine type with a given key name."""
        self._register_types(
            "Search engine",
            self.registered_search_engine_types,
            BaseSearchEngine,
            name,
            cls,
        )

    def aggregator_type(self, name: str) -> type[BaseAggregator]:
        """Return a decorator to register an aggregator type with a given key name."""
        return lambda cls: self.register_aggregator_type(name, cls)

    def register_aggregator_type(self, name: str, cls: type[BaseAggregator]) -> None:
        """Register an aggregator type with a given key name."""
        self._register_types(
            "Aggregator",
            self.registered_aggregator_types,
            BaseAggregator,
            name,
            cls,
        )

    def ai_client_type(self, name: str) -> type[BaseAIClient]:
        """Return a decorator to register an AI client type with a given key name."""
        return lambda cls: self.register_ai_client_type(name, cls)

    def register_ai_client_type(
        self,
        name: str,
        cls: type[BaseAIClient],
    ) -> None:
        """Register an AI client type with a given key name."""
        self._register_types(
            "AI client",
            self.registered_ai_client_types,
            BaseAIClient,
            name,
            cls,
        )

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

        type_registries_to_check = [
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

    def build_query(self, query: str) -> list[dict]:
        """Generate the query based on the spec."""
        response = self.ai_client.response(
            self._build_messages(query),
            self.format_model,
        )

        try:
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

    def search(self, query: str) -> SearchResult:
        """Search for the query."""
        search_queries = self.build_query(query)
        search_results = []
        for search_query in search_queries:
            result = {}
            for index in self.indexs:
                search_engine_arguments = index.search_engine_arguments_type(
                    **search_query[index.name],
                )
                search_result = index.search_engine.search(
                    search_engine_arguments,
                )
                result[index.name] = search_result
            search_results.append(result)

        return search_results

    def run(self, query: str) -> BaseAggregatorResult:
        """Execute the query and return the aggregated result."""
        return self.aggregator.aggregate(self.search(query))
