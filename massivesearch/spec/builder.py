"""Spec builder for massivesearch."""

from inspect import signature

from pydantic import BaseModel, create_model

from massivesearch.aggregator.base import BaseAggregator
from massivesearch.index.base import BaseIndex
from massivesearch.search_engine.base import BaseSearchEngine
from massivesearch.spec.spec import Spec, SpecIndexUnit
from massivesearch.spec.validator import spec_validator, validate_search_engine

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
        indexs: dict[str, type[BaseIndex]] | None = None,
        search_engines: dict[str, type[BaseSearchEngine]] | None = None,
        aggregators: dict[str, type[BaseAggregator]] | None = None,
    ) -> None:
        """Initialize the SpecBuilder with an empty specification."""
        self.spec_units: dict[str, SpecIndexUnit] = {}
        self.registered_indexs: dict[str, type[BaseIndex]] = {}
        self.registered_search_engines: dict[str, type[BaseSearchEngine]] = {}
        self.registered_aggregators: dict[str, type[BaseAggregator]] = {}

        for name, index in (indexs or {}).items():
            self.register_index_type(name, index)
        for name, search_engine in (search_engines or {}).items():
            self.register_search_engine_type(name, search_engine)
        for name, aggregator in (aggregators or {}).items():
            self.register_aggregator_type(name, aggregator)

        self.spec_aggregator: BaseAggregator | None = None

    def include(self, spec: dict) -> None:
        """Include a dictionary of schemas to the spec."""
        if not spec:
            msg = "No schemas available to include."
            raise ValueError(msg)

        spec_validator(
            spec,
            self.registered_indexs,
            self.registered_search_engines,
            self.registered_aggregators,
        )

        index_spec = spec.get("indexs")

        for index in index_spec:
            name = index.get("name")
            index_type = index.get("type")
            search_engine = index.get("search_engine")
            search_engine_type = search_engine.get("type")
            self.add_index_spec(
                name,
                index_type=index_type,
                index_arguments=index,
                search_engine_type=search_engine_type,
                search_engine_arguments=search_engine,
            )

        aggregator_spec = spec.get("aggregator")
        if aggregator_spec:
            aggregator_type = aggregator_spec.get("type")
            self.set_aggregator_spec(
                aggregator_type=aggregator_type,
                aggregator_arguments=aggregator_spec,
            )

    def add_index_spec(
        self,
        name: str,
        *,
        index_type: str,
        index_arguments: dict,
        search_engine_type: str,
        search_engine_arguments: dict,
    ) -> None:
        """Add a new index and search engine to the spec."""
        if not name:
            msg = "Name cannot be empty."
            raise ValueError(msg)
        if not index_type:
            msg = "Index type cannot be empty."
            raise ValueError(msg)
        if not search_engine_type:
            msg = "Search engine type cannot be empty."
            raise ValueError(msg)

        if name in self.spec_units:
            msg = f"Spec with name '{name}' already exists."
            raise ValueError(msg)

        index = self.registered_indexs[index_type](**index_arguments)
        search_engine = self.registered_search_engines[search_engine_type](
            **search_engine_arguments,
        )
        self.spec_units[name] = SpecIndexUnit(
            index=index,
            search_engine=search_engine,
            search_engine_arguments_type=self._get_arguments_type(search_engine),
        )

    def set_aggregator_spec(
        self,
        *,
        aggregator_type: str,
        aggregator_arguments: dict,
    ) -> None:
        """Set the aggregator for the spec."""
        if not aggregator_type:
            msg = "Aggregator type cannot be empty."
            raise ValueError(msg)

        if aggregator_type not in self.registered_aggregators:
            msg = f"Aggregator type '{aggregator_type}' is unknown."
            raise ValueError(msg)

        self.spec_aggregator = self.registered_aggregators[aggregator_type](
            **aggregator_arguments or {},
        )

    def build_prompt(self) -> str:
        """Build the prompt for the spec."""
        if not self.spec_units:
            msg = "No schemas available to build a prompt."
            raise ValueError(msg)

        index_context = "\n".join(
            spec_unit.index.prompt(name) for name, spec_unit in self.spec_units.items()
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
        if not self.spec_units or not self.registered_search_engines:
            msg = "No spec units or search engines available to build format."
            raise ValueError(msg)

        fields = {}
        for name, spec_unit in self.spec_units.items():
            arguments_type = self._get_arguments_type(spec_unit.search_engine)

            fields[name] = (arguments_type, ...)

        single_query_format = create_model("SingleQueryFormat", **fields)
        return create_model(
            "MultiQueryFormat",
            queries=list[single_query_format],
        )

    @property
    def spec(self) -> Spec:
        """Return the spec."""
        return Spec(
            indexs=self.spec_units,
            aggregator=self.spec_aggregator,
            prompt_message=self.build_prompt(),
            query_model=self.build_format(),
        )

    def index(self, name: str) -> type[BaseIndex]:
        """Register a index with a given key name."""

        def decorator(cls: type[BaseIndex]) -> type[BaseIndex]:
            if name in self.registered_indexs:
                msg = f"Index with name '{name}' is already registered."
                raise ValueError(msg)
            self.registered_indexs[name] = cls

            return cls

        return decorator

    def register_index_type(self, name: str, index: type[BaseIndex]) -> None:
        """Add a new index to the spec."""
        if not name:
            msg = "Name cannot be empty."
            raise ValueError(msg)
        if not index:
            msg = "Index cannot be empty."
            raise ValueError(msg)

        if issubclass(index, BaseIndex) is False:
            msg = f"Index '{name}' is not a subclass of BaseIndex."
            raise TypeError(msg)

        if name in self.registered_indexs:
            msg = f"Index with name '{name}' already exists."
            raise ValueError(msg)

        self.registered_indexs[name] = index

    def search_engine(self, name: str) -> type[BaseSearchEngine]:
        """Register a search engine with a given key name."""

        def decorator(cls: type[BaseSearchEngine]) -> type:
            if name in self.registered_search_engines:
                msg = f"Search engine with name '{name}' is already registered."
                raise ValueError(msg)
            validate_search_engine(cls)
            self.registered_search_engines[name] = cls
            return cls

        return decorator

    def register_search_engine_type(
        self,
        name: str,
        search_engine: type[BaseSearchEngine],
    ) -> None:
        """Add a new search engine to the spec."""
        if not name:
            msg = "Name cannot be empty."
            raise ValueError(msg)
        if not search_engine:
            msg = "Search engine cannot be empty."
            raise ValueError(msg)

        if issubclass(search_engine, BaseSearchEngine) is False:
            msg = f"Search engine '{name}' is not a subclass of BaseSearchEngine."
            raise TypeError(msg)

        if name in self.registered_search_engines:
            msg = f"Search engine with name '{name}' already exists."
            raise ValueError(msg)

        self.registered_search_engines[name] = search_engine

    def aggregator(self, name: str) -> type[BaseAggregator]:
        """Register an aggregator with a given key name."""

        def decorator(cls: type[BaseAggregator]) -> type:
            if name in self.registered_aggregators:
                msg = f"Aggregator with name '{name}' is already registered."
                raise ValueError(msg)
            self.registered_aggregators[name] = cls
            return cls

        return decorator

    def register_aggregator_type(
        self,
        name: str,
        aggregator: type[BaseAggregator],
    ) -> None:
        """Add a new aggregator to the spec."""
        if not name:
            msg = "Name cannot be empty."
            raise ValueError(msg)
        if not aggregator:
            msg = "Aggregator cannot be empty."
            raise ValueError(msg)

        if issubclass(aggregator, BaseAggregator) is False:
            msg = f"Aggregator '{name}' is not a subclass of BaseAggregator."
            raise TypeError(msg)

        if name in self.registered_aggregators:
            msg = f"Aggregator with name '{name}' already exists."
            raise ValueError(msg)

        self.registered_aggregators[name] = aggregator

    def __or__(self, other: "SpecBuilder") -> "SpecBuilder":
        """Combine two SpecBuilders using the | operator."""
        if not isinstance(other, SpecBuilder):
            msg = f"Cannot combine SpecBuilder with {type(other)}."
            raise TypeError(msg)

        overlap_spec_units = set(self.spec_units.keys()) & set(other.spec_units.keys())
        if overlap_spec_units:
            msg = f"SpecBuilder has overlapping spec_units: {overlap_spec_units}."
            raise ValueError(msg)

        overlap_registered_indexs = set(self.registered_indexs.keys()) & set(
            other.registered_indexs.keys(),
        )
        if overlap_registered_indexs:
            msg = (
                f"SpecBuilder has overlapping registered_indexs: "
                f"{overlap_registered_indexs}."
            )
            raise ValueError(msg)

        overlap_registered_search_engines = set(
            self.registered_search_engines.keys(),
        ) & set(other.registered_search_engines.keys())
        if overlap_registered_search_engines:
            msg = (
                "SpecBuilder has overlapping registered_search_engines: "
                f"{overlap_registered_search_engines}."
            )
            raise ValueError(msg)

        overlap_registered_aggregators = set(
            self.registered_aggregators.keys(),
        ) & set(other.registered_aggregators.keys())
        if overlap_registered_aggregators:
            msg = (
                "SpecBuilder has overlapping registered_aggregators: "
                f"{overlap_registered_aggregators}."
            )
            raise ValueError(msg)

        if self.spec_aggregator and other.spec_aggregator:
            msg = "SpecBuilder has overlapping spec_aggregators."
            raise ValueError(msg)

        combined_spec_units = {**self.spec_units, **other.spec_units}
        combined_registered_indexs = {
            **self.registered_indexs,
            **other.registered_indexs,
        }
        combined_registered_search_engines = {
            **self.registered_search_engines,
            **other.registered_search_engines,
        }
        combined_registered_aggregators = {
            **self.registered_aggregators,
            **other.registered_aggregators,
        }
        combined_spec_builder = SpecBuilder()
        combined_spec_builder.spec_units = combined_spec_units
        combined_spec_builder.registered_indexs = combined_registered_indexs
        combined_spec_builder.registered_search_engines = (
            combined_registered_search_engines
        )
        combined_spec_builder.registered_aggregators = combined_registered_aggregators
        combined_spec_builder.spec_aggregator = (
            self.spec_aggregator or other.spec_aggregator
        )
        return combined_spec_builder
