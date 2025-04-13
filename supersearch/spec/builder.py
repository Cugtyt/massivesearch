"""Spec builder for supersearch."""

from inspect import signature

from pydantic import BaseModel, create_model

from supersearch.index import registered_indexs
from supersearch.index.base import BaseIndex
from supersearch.model.azure_openai import AzureOpenAIClient
from supersearch.model.base import BaseModelClient
from supersearch.search_engine import registered_search_engines
from supersearch.search_engine.base_engine import BaseSearchEngine
from supersearch.spec.spec_validator import spec_validator

STSTEM_PROMPT_TEMPLATE = """Fill the serch engine arguments based on the user's intent
and current index information.

{context}
"""


class SpecBuilder:
    """A builder for constructing and managing index schema specifications."""

    def __init__(
        self,
        index_spec: dict[str, BaseIndex] | None = None,
        search_engine_spec: dict[str, BaseSearchEngine] | None = None,
        model_client: BaseModelClient | None = None,
    ) -> None:
        """Initialize the SpecBuilder with an empty specification."""
        self.index_spec: dict[str, BaseIndex] = index_spec or {}
        self.search_engine_spec: dict[str, BaseSearchEngine] = search_engine_spec or {}
        if self.index_spec.keys() != self.search_engine_spec.keys():
            msg = "Index spec and search engine spec keys do not match."
            raise ValueError(msg)

        self.model_client = model_client or AzureOpenAIClient()

    def include(self, spec: dict) -> None:
        """Include a dictionary of schemas to the spec."""
        if not spec:
            msg = "No schemas available to include."
            raise ValueError(msg)

        spec_validator(spec)

        for name, schema in spec.items():
            index_schema = schema.get("index")
            index_type = index_schema.get("type")
            search_engine = schema.get("search_engine")
            search_engine_type = search_engine.get("type")
            self.add(
                name,
                registered_indexs[index_type](**index_schema),
                registered_search_engines[search_engine_type](**search_engine),
            )

    def add(
        self,
        name: str,
        index: BaseIndex,
        search_engine: BaseSearchEngine,
    ) -> None:
        """Add a schema to the spec."""
        self.index_spec[name] = index
        self.search_engine_spec[name] = search_engine

    def build_prompt(self, query: str) -> list[dict[str, str]]:
        """Build the prompt for the spec."""
        if not self.index_spec:
            msg = "No schemas available to build a prompt."
            raise ValueError(msg)

        index_context = "\n".join(
            schema.schema_prompt(name) for name, schema in self.index_spec.items()
        )
        return [
            {
                "role": "system",
                "content": STSTEM_PROMPT_TEMPLATE.format(context=index_context),
            },
            {
                "role": "user",
                "content": query,
            },
        ]

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

    def build_format(self) -> type[BaseModel]:
        """Format the search engine arguments format."""
        if not self.search_engine_spec:
            msg = "No search engine schemas available to build a format."
            raise ValueError(msg)

        fields = {}
        for name, search_engine in self.search_engine_spec.items():
            arguments_type = self._get_arguments_type(search_engine)
            fields[name] = arguments_type

        return create_model(
            "SearchEngineArguments",
            **fields,
        )

    def query(self, query: str) -> dict:
        """Query based on the spec."""
        if not self.index_spec:
            msg = "No schemas available to query."
            raise ValueError(msg)

        if not query:
            msg = "Query string cannot be empty."
            raise ValueError(msg)

        return self.model_client.response(
            self.build_prompt(query),
            self.build_format(),
        )
