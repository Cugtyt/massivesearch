"""Tests for SpecBuilder."""

from pathlib import Path
from unittest.mock import MagicMock

import pytest
import yaml
from pydantic import BaseModel

from supersearch.index import (
    bool_index_spec_builder,
    date_index_spec_builder,
    number_index_spec_builder,
    text_index_spec_builder,
    vector_index_spec_builder,
)
from supersearch.index.number import NumberIndex
from supersearch.index.text import TextIndex
from supersearch.search_engine import (
    bool_search_engine_spec_builder,
    date_search_engine_spec_builder,
    number_search_engine_spec_builder,
    text_search_engine_spec_builder,
    vector_search_engine_spec_builder,
)
from supersearch.search_engine.text_engine import (
    TextSearchEngine,
    TextSearchEngineConfig,
)
from supersearch.spec import (
    BaseIndex,
    BaseSearchEngine,
    BaseSearchEngineArguments,
    BaseSearchEngineConfig,
    BaseSearchResult,
    SpecBuilder,
    SpecUnit,
)


def test_spec_builder_default_init() -> None:
    """Test SpecBuilder default initialization."""
    builder = SpecBuilder()
    if builder.spec_units != {}:
        msg = "Expected builder.spec_units to be an empty dictionary."
        raise ValueError(msg)
    if builder.registered_indexs != {}:
        msg = "Expected builder.registered_indexs to be an empty dictionary."
        raise ValueError(msg)
    if builder.registered_search_engines != {}:
        msg = "Expected builder.registered_search_engines to be an empty dictionary."
        raise ValueError(msg)


def test_spec_builder_init_with_index_and_engine() -> None:
    """Test SpecBuilder initialization with index and search engine."""
    b = text_index_spec_builder | text_search_engine_spec_builder

    builder = SpecBuilder(
        indexs=b.registered_indexs,
        search_engines=b.registered_search_engines,
    )
    if len(builder.registered_indexs) != 1:
        msg = "Expected builder.registered_indexs to contain one item."
        raise ValueError(msg)
    if len(builder.registered_search_engines) != 1:
        msg = "Expected builder.registered_search_engines to contain one item."
        raise ValueError(msg)


def test_spec_builder_add() -> None:
    """Test adding schemas to SpecBuilder."""
    builder = SpecBuilder()
    text_index = TextIndex(
        description="A text schema.",
        examples=["example1", "example2"],
    )
    text_search_engine = TextSearchEngine(
        config=TextSearchEngineConfig(),
    )
    builder.add("text_schema", text_index, text_search_engine)

    if "text_schema" not in builder.spec_units:
        msg = '"text_schema" not found in builder.spec_units'
        raise ValueError(msg)
    if builder.spec_units["text_schema"].index != text_index:
        msg = "Expected builder.spec_units['text_schema'].index to match text_index."
        raise ValueError(msg)
    if builder.spec_units["text_schema"].search_engine != text_search_engine:
        msg = (
            "Expected builder.spec_units['text_schema'].search_engine to match "
            "mock_search_engine."
        )
        raise ValueError(msg)


def test_spec_builder_include() -> None:
    """Test SpecBuilder initialization via include method from a YAML file."""
    spec_file_path = Path("./test/spec/test_spec.yaml")

    with spec_file_path.open() as file:
        valid_spec = yaml.safe_load(file)

    builder = (
        bool_index_spec_builder
        | date_index_spec_builder
        | number_index_spec_builder
        | text_index_spec_builder
        | vector_index_spec_builder
        | bool_search_engine_spec_builder
        | date_search_engine_spec_builder
        | number_search_engine_spec_builder
        | text_search_engine_spec_builder
        | vector_search_engine_spec_builder
    )
    builder.include(valid_spec)

    if len(builder.spec_units) != len(valid_spec):
        msg = (
            f"Expected {len(valid_spec)} spec units, but got {len(builder.spec_units)}."
        )
        raise ValueError(msg)

    for key in valid_spec:
        if key not in builder.spec_units:
            msg = f"Key '{key}' not found in builder.spec_units."
            raise KeyError(msg)
        if not isinstance(builder.spec_units[key], SpecUnit):
            msg = f"Expected builder.spec_units['{key}'] to be an instance of SpecUnit."
            raise TypeError(msg)
        if (
            type(builder.spec_units[key].index)
            not in builder.registered_indexs.values()
        ):
            msg = f"Expected builder.spec_units['{key}'].index to match mock_index."
            raise ValueError(msg)
        if (
            type(builder.spec_units[key].search_engine)
            not in builder.registered_search_engines.values()
        ):
            msg = (
                f"Expected builder.spec_units['{key}'].search_engine to match "
                f"mock_engine."
            )
            raise ValueError(msg)


def test_spec_builder_build_prompt() -> None:
    """Test building a prompt with SpecBuilder."""
    spec_file_path = Path("./test/spec/test_spec.yaml")

    with spec_file_path.open() as file:
        valid_spec = yaml.safe_load(file)

    builder = (
        bool_index_spec_builder
        | date_index_spec_builder
        | number_index_spec_builder
        | text_index_spec_builder
        | vector_index_spec_builder
        | bool_search_engine_spec_builder
        | date_search_engine_spec_builder
        | number_search_engine_spec_builder
        | text_search_engine_spec_builder
        | vector_search_engine_spec_builder
    )
    builder.include(valid_spec)
    prompt = builder.build_prompt()

    if "Fill the search engine query arguments" not in prompt:
        msg = "Expected 'Fill the search engine query arguments' to be in the prompt."
        raise ValueError(
            msg,
        )
    if "high-performance laptop" not in prompt:
        msg = "Expected 'high-performance laptop' to be in the prompt."
        raise ValueError(msg)


def test_spec_builder_build_format() -> None:
    """Test building a format with SpecBuilder."""
    builder = (
        bool_index_spec_builder
        | date_index_spec_builder
        | number_index_spec_builder
        | text_index_spec_builder
        | vector_index_spec_builder
        | bool_search_engine_spec_builder
        | date_search_engine_spec_builder
        | number_search_engine_spec_builder
        | text_search_engine_spec_builder
        | vector_search_engine_spec_builder
    )
    spec_file_path = Path("./test/spec/test_spec.yaml")

    with spec_file_path.open() as file:
        valid_spec = yaml.safe_load(file)

    builder.include(valid_spec)

    format_model = builder.build_format()

    if not issubclass(format_model, BaseModel):
        msg = "Expected format_model to be a subclass of Pydantic BaseModel."
        raise TypeError(msg)

    if format_model.__name__ != "MultiQueryFormat":
        msg = "Expected format_model name to be 'MultiQueryFormat'."
        raise ValueError(msg)

    if (
        len(format_model.model_fields) == 1
        and "queries" not in format_model.model_fields
    ):
        msg = "Expected format_model to have 'queries' field."
        raise AttributeError(msg)

    if (
        format_model.model_fields["queries"].annotation.__name__ != "list"
        and format_model.model_fields["queries"].annotation.__args__[0].__name__
        != "SingleQueryFormat"
    ):
        msg = "Expected format_model.queries type is list[SingleQueryFormat]."
        raise TypeError(msg)


def test_spec_builder_register_index() -> None:
    """Test registering an index using the decorator."""
    builder = SpecBuilder()

    @builder.index("test_index")
    class TestIndex(BaseIndex):
        pass

    if "test_index" not in builder.registered_indexs:
        msg = "'test_index' not found in builder.registered_indexs"
        raise KeyError(msg)
    if builder.registered_indexs["test_index"] != TestIndex:
        msg = "Expected builder.registered_indexs['test_index'] to be TestIndex"
        raise ValueError(
            msg,
        )


def test_spec_builder_register_search_engine() -> None:
    """Test registering a search engine using the decorator."""
    builder = SpecBuilder()

    class TestSearchEngineConfig(BaseSearchEngineConfig):
        pass

    class TestSearchEngineArguments(BaseSearchEngineArguments):
        pass

    @builder.search_engine("test_engine")
    class TestSearchEngine(BaseSearchEngine):
        config: TextSearchEngineConfig

        def search(self, arguments: TestSearchEngineArguments) -> BaseSearchResult:
            return MagicMock(spec=BaseSearchResult)

    if "test_engine" not in builder.registered_search_engines:
        msg = "'test_engine' not found in builder.registered_search_engines"
        raise KeyError(msg)
    if builder.registered_search_engines["test_engine"] != TestSearchEngine:
        msg = (
            "Expected builder.registered_search_engines['test_engine'] to be "
            "TestSearchEngine"
        )
        raise ValueError(
            msg,
        )


def test_spec_builder_or_operator() -> None:
    """Test combining two SpecBuilders using the | operator."""
    builder1 = SpecBuilder()
    builder2 = SpecBuilder()

    text_index = TextIndex(description="Text schema", examples=["example"])
    number_index = NumberIndex(
        description="Number schema",
        range={"min": 0, "max": 100},
        examples=[10],
    )
    mock_engine1 = MagicMock(spec=BaseSearchEngine)
    mock_engine2 = MagicMock(spec=BaseSearchEngine)

    builder1.add("text_schema", text_index, mock_engine1)
    builder2.add("number_schema", number_index, mock_engine2)

    combined = builder1 | builder2

    if "text_schema" not in combined.spec_units:
        msg = "'text_schema' not found in combined.spec_units"
        raise KeyError(msg)
    if "number_schema" not in combined.spec_units:
        msg = "'number_schema' not found in combined.spec_units"
        raise KeyError(msg)
    if combined.spec_units["text_schema"].index != text_index:
        msg = "Expected combined.spec_units['text_schema'].index to match text_index"
        raise ValueError(
            msg,
        )
    if combined.spec_units["number_schema"].index != number_index:
        msg = (
            "Expected combined.spec_units['number_schema'].index to match number_index"
        )
        raise ValueError(
            msg,
        )


def test_spec_builder_or_operator_with_overlaps() -> None:
    """Test that combining SpecBuilders with overlapping keys raises an error."""
    builder1 = SpecBuilder()
    builder2 = SpecBuilder()

    # Add the same key to both builders
    mock_index = MagicMock(spec=BaseIndex)
    mock_engine = MagicMock(spec=BaseSearchEngine)

    builder1.add("same_key", mock_index, mock_engine)
    builder2.add("same_key", mock_index, mock_engine)

    # Combining should raise an error
    with pytest.raises(ValueError, match="overlapping spec_units"):
        _ = builder1 | builder2


def test_spec_builder_empty_spec_error() -> None:
    """Test error when SpecBuilder has no schemas."""
    builder = SpecBuilder()

    with pytest.raises(
        ValueError,
        match="No schemas available to build a prompt.",
    ):
        builder.build_prompt()
