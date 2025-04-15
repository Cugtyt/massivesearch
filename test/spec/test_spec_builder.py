"""Tests for SpecBuilder."""

from pathlib import Path
from unittest.mock import MagicMock

import pytest
import yaml
from pydantic import BaseModel

from massivesearch.index.base import BaseIndex
from massivesearch.search_engine.base import (
    BaseSearchEngine,
    BaseSearchEngineArguments,
    BaseSearchResultIndex,
)
from massivesearch.spec import (
    SpecBuilder,
    SpecIndexUnit,
)
from test.index import (
    bool_index_spec_builder,
    date_index_spec_builder,
    number_index_spec_builder,
    text_index_spec_builder,
    vector_index_spec_builder,
)
from test.index.number import NumberIndex
from test.index.text import TextIndex
from test.search_engine import (
    bool_search_engine_spec_builder,
    date_search_engine_spec_builder,
    number_search_engine_spec_builder,
    text_search_engine_spec_builder,
    vector_search_engine_spec_builder,
)
from test.search_engine.number_engine import (
    NumberSearchEngine,
)
from test.search_engine.text_engine import (
    TextSearchEngine,
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
        matching_strategy="exact",
    )
    builder.add_index("text_schema", text_index, text_search_engine)

    if "text_schema" not in builder.spec_units:
        msg = '"text_schema" not found in builder.spec_units'
        raise ValueError(msg)
    spec_unit = builder.spec_units["text_schema"]
    if spec_unit.index != text_index:
        msg = "Expected builder.spec_units['text_schema'].index to match text_index."
        raise ValueError(msg)
    if spec_unit.search_engine != text_search_engine:
        msg = (
            "Expected builder.spec_units['text_schema'].search_engine to match "
            "text_search_engine."
        )
        raise ValueError(msg)
    if spec_unit.search_engine_arguments_type is None:
        msg = "Expected search_engine_arguments_type to be set."
        raise ValueError(msg)
    if builder.registered_indexs:
        msg = "Expected builder.registered_indexs to be empty after add."
        raise ValueError(msg)
    if builder.registered_search_engines:
        msg = "Expected builder.registered_search_engines to be empty after add."
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

    if len(builder.spec_units) != len(valid_spec["indexs"]):
        msg = (
            f"Expected {len(valid_spec)} spec units, but got {len(builder.spec_units)}."
        )
        raise ValueError(msg)

    for index in valid_spec["indexs"]:
        key = index["name"]
        if key not in builder.spec_units:
            msg = f"Key '{key}' not found in builder.spec_units."
            raise KeyError(msg)
        if not isinstance(builder.spec_units[key], SpecIndexUnit):
            msg = (
                f"Expected builder.spec_units['{key}'] to be an instance of "
                f"SpecIndexUnit."
            )
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

    class TestSearchEngineArguments(BaseSearchEngineArguments):
        pass

    @builder.search_engine("test_engine")
    class TestSearchEngine(BaseSearchEngine):
        def search(self, arguments: TestSearchEngineArguments) -> BaseSearchResultIndex:  # noqa: ARG002
            return MagicMock(spec=BaseSearchResultIndex)

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

    @builder1.index("text")
    class TestTextIndex(TextIndex):
        pass

    @builder1.search_engine("text_engine")
    class TestTextSearchEngine(TextSearchEngine):
        pass

    @builder2.index("number")
    class TestNumberIndex(NumberIndex):
        pass

    @builder2.search_engine("number_engine")
    class TestNumberSearchEngine(NumberSearchEngine):
        pass

    text_index = TestTextIndex(description="Text schema", examples=["example"])
    number_index = TestNumberIndex(
        description="Number schema",
        range={"min": 0, "max": 100},
        examples=[10],
    )
    text_search_engine = TestTextSearchEngine(
        matching_strategy="exact",
    )
    number_search_engine = TestNumberSearchEngine()

    builder1.add_index("text_schema", text_index, text_search_engine)
    builder2.add_index("number_schema", number_index, number_search_engine)

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

    if "text" not in combined.registered_indexs:
        msg = "'text' index not found in combined.registered_indexs"
        raise KeyError(msg)
    if "number" not in combined.registered_indexs:
        msg = "'number' index not found in combined.registered_indexs"
        raise KeyError(msg)
    if "text_engine" not in combined.registered_search_engines:
        msg = "'text_engine' not found in combined.registered_search_engines"
        raise KeyError(msg)
    if "number_engine" not in combined.registered_search_engines:
        msg = "'number_engine' not found in combined.registered_search_engines"
        raise KeyError(msg)


def test_spec_builder_or_operator_with_overlaps() -> None:
    """Test that combining SpecBuilders with overlapping keys raises an error."""
    builder1 = SpecBuilder()
    builder2 = SpecBuilder()

    @builder1.index("same_index")
    class TestIndex1(TextIndex):
        pass

    @builder1.search_engine("same_engine")
    class TestEngine1(TextSearchEngine):
        pass

    @builder2.index("same_index")
    class TestIndex2(NumberIndex):
        pass

    @builder2.search_engine("same_engine")
    class TestEngine2(NumberSearchEngine):
        pass

    text_index = TestIndex1(
        description="Text schema",
        examples=["example"],
    )
    text_search_engine = TestEngine1(
        matching_strategy="exact",
    )

    builder1_spec = SpecBuilder()
    builder2_spec = SpecBuilder()
    builder1_spec.add_index("same_key", text_index, text_search_engine)
    builder2_spec.add_index("same_key", text_index, text_search_engine)
    with pytest.raises(ValueError, match="overlapping spec_units"):
        _ = builder1_spec | builder2_spec

    builder1_reg_idx = SpecBuilder()
    builder2_reg_idx = SpecBuilder()

    @builder1_reg_idx.index("overlap_idx")
    class _Idx1(BaseIndex):
        pass

    @builder2_reg_idx.index("overlap_idx")
    class _Idx2(BaseIndex):
        pass

    with pytest.raises(ValueError, match="overlapping registered_indexs"):
        _ = builder1_reg_idx | builder2_reg_idx

    builder1_reg_eng = SpecBuilder()
    builder2_reg_eng = SpecBuilder()

    @builder1_reg_eng.search_engine("overlap_eng")
    class _Eng1(BaseSearchEngine):
        def search(self, arguments: BaseSearchEngineArguments) -> BaseSearchResultIndex:
            pass

    @builder2_reg_eng.search_engine("overlap_eng")
    class _Eng2(BaseSearchEngine):
        def search(self, arguments: BaseSearchEngineArguments) -> BaseSearchResultIndex:
            pass

    with pytest.raises(ValueError, match="overlapping registered_search_engines"):
        _ = builder1_reg_eng | builder2_reg_eng


def test_spec_builder_empty_spec_error() -> None:
    """Test error when SpecBuilder has no schemas."""
    builder = SpecBuilder()

    with pytest.raises(
        ValueError,
        match="No schemas available to build a prompt.",
    ):
        builder.build_prompt()
