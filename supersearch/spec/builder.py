"""Spec builder for supersearch."""

from inspect import signature

from pydantic import BaseModel, create_model

from supersearch.index import registered_indexs
from supersearch.index.base import BaseIndex
from supersearch.search_engine import registered_search_engines
from supersearch.search_engine.base_engine import BaseSearchEngine
from supersearch.spec.spec import Spec
from supersearch.spec.validator import spec_validator

STSTEM_PROMPT_TEMPLATE = """Fill the search engine query arguments
based on the user's intent and current index information.

You will break down the user's intent into one or multiple queries,
and each query will be passed to the search engine.
These queries will be executed in parallel and aggregated.
Every query in the array represents an independent search path.

The relationship between different queries in the array is OR -
results matching ANY of the queries will be included in the final results.

Within each individual query, parameters have an AND relationship -
all conditions within a single query must be satisfied simultaneously.

For example, with a query array of 5 elements, where each element contains
3 parameters:
- Query 1: (param1 AND param2 AND param3)
- Query 2: (param1 AND param2 AND param3)
- Query 3: (param1 AND param2 AND param3)
- Query 4: (param1 AND param2 AND param3)
- Query 5: (param1 AND param2 AND param3)

The final search logic is:
(Query 1) OR (Query 2) OR (Query 3) OR (Query 4) OR (Query 5)

This structure allows you to create complex search patterns that capture
different aspects of the user's intent while maintaining logical clarity.

The following is the index information:

{context}
"""


class SpecBuilder:
    """A builder for constructing and managing index schema specifications."""

    def __init__(
        self,
        index_spec: dict[str, BaseIndex] | None = None,
        search_engine_spec: dict[str, BaseSearchEngine] | None = None,
    ) -> None:
        """Initialize the SpecBuilder with an empty specification."""
        self.index_spec: dict[str, BaseIndex] = index_spec or {}
        self.search_engine_spec: dict[str, BaseSearchEngine] = search_engine_spec or {}
        if self.index_spec.keys() != self.search_engine_spec.keys():
            msg = "Index spec and search engine spec keys do not match."
            raise ValueError(msg)

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

    def build_prompt(self) -> str:
        """Build the prompt for the spec."""
        if not self.index_spec:
            msg = "No schemas available to build a prompt."
            raise ValueError(msg)

        index_context = "\n".join(
            schema.schema_prompt(name) for name, schema in self.index_spec.items()
        )
        return STSTEM_PROMPT_TEMPLATE.format(context=index_context)

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

        single_query_format = create_model("SingleQueryFormat", **fields)
        return create_model(
            "MultiQueryFormat",
            queries=list[single_query_format],
        )

    @property
    def spec(self) -> Spec:
        """Return the spec."""
        if not self.index_spec:
            msg = "No schemas available to build the spec."
            raise ValueError(msg)
        if not self.search_engine_spec:
            msg = "No search engine schemas available to build the spec."
            raise ValueError(msg)
        return Spec(
            index_spec=self.index_spec,
            search_engine_spec=self.search_engine_spec,
            prompt_message=self.build_prompt(),
            format_model=self.build_format(),
        )
