"""Tests for SpecBuilder."""

from pathlib import Path
from unittest.mock import MagicMock

import pytest
import yaml

from supersearch.index import NumberIndex, TextIndex
from supersearch.index.base import BaseIndex
from supersearch.search_engine.base_engine import BaseSearchEngine
from supersearch.search_engine.text_engine import (
    TextSearchEngine,
    TextSearchEngineArguments,
    TextSearchEngineConfig,
)
from supersearch.spec.builder import SpecBuilder


def test_spec_builder_default_init() -> None:
    """Test SpecBuilder default initialization."""
    builder = SpecBuilder()
    if builder.index_spec != {}:
        msg = "Expected empty index_spec on default init."
        raise TypeError(msg)
    if builder.search_engine_spec != {}:
        msg = "Expected empty search_engine_spec on default init."
        raise ValueError(msg)


def test_spec_builder_init_with_spec() -> None:
    """Test SpecBuilder initialization with provided specs."""
    mock_index = MagicMock(spec=BaseIndex)
    mock_engine = MagicMock(spec=BaseSearchEngine)
    builder_with_spec = SpecBuilder(
        index_spec={"key": mock_index},
        search_engine_spec={"key": mock_engine},
    )
    if builder_with_spec.index_spec != {"key": mock_index}:
        msg = "index_spec not initialized correctly."
        raise ValueError(msg)
    if builder_with_spec.search_engine_spec != {"key": mock_engine}:
        msg = "search_engine_spec not initialized correctly."
        raise ValueError(msg)


def test_spec_builder_init_from_file() -> None:
    """Test SpecBuilder initialization via include method from a YAML file."""
    spec_file_path = Path("./test/spec/test_spec.yaml")

    with spec_file_path.open() as file:
        valid_spec = yaml.safe_load(file)

    builder_from_file = SpecBuilder()
    builder_from_file.include(valid_spec)

    if not builder_from_file.index_spec:
        msg = "index_spec should be populated from file."
        raise ValueError(msg)
    if not builder_from_file.search_engine_spec:
        msg = "search_engine_spec should be populated from file."
        raise ValueError(msg)

    if len(builder_from_file.index_spec) != len(valid_spec):
        msg = (
            f"Expected index_spec length "
            f"({len(builder_from_file.index_spec)}) to match "
            f"valid_spec length ({len(valid_spec)})."
        )
        raise ValueError(msg)

    if (
        builder_from_file.index_spec.keys()
        != builder_from_file.search_engine_spec.keys()
    ):
        msg = (
            f"index_spec keys ({builder_from_file.index_spec.keys()}) and "
            f"search_engine_spec keys ({builder_from_file.search_engine_spec.keys()}) "
            "should match."
        )
        raise ValueError(msg)

    for key in valid_spec:
        if key not in builder_from_file.index_spec:
            msg = f"Key '{key}' from yaml missing in index_spec."
            raise ValueError(msg)
        if key not in builder_from_file.search_engine_spec:
            msg = f"Key '{key}' from yaml missing in search_engine_spec."
            raise ValueError(msg)
        if not isinstance(builder_from_file.index_spec[key], BaseIndex):
            msg = f"Value for key '{key}' in index_spec is not a BaseIndex instance."
            raise TypeError(msg)
        if not isinstance(builder_from_file.search_engine_spec[key], BaseSearchEngine):
            msg = (
                f"Value for key '{key}' in search_engine_spec is not a "
                f"BaseSearchEngine instance."
            )
            raise TypeError(msg)


def test_spec_builder_add() -> None:
    """Test adding schemas to SpecBuilder."""
    builder = SpecBuilder()
    text_index = TextIndex(
        description="A text schema.",
        examples=["example1", "example2"],
    )
    mock_search_engine = MagicMock()
    builder.add("text_schema", text_index, mock_search_engine)
    if "text_schema" not in builder.index_spec:
        msg = "'text_schema' not found in builder.index_spec"
        raise ValueError(msg)
    if builder.index_spec["text_schema"] != text_index:
        msg = (
            "The 'text_schema' in builder.index_spec does not match "
            "the expected schema."
        )
        raise TypeError(msg)
    if builder.search_engine_spec["text_schema"] != mock_search_engine:
        msg = (
            "The 'text_schema' in builder.search_engine_spec does not match "
            "the expected search engine."
        )
        raise ValueError(msg)


def test_spec_builder_build_prompt() -> None:
    """Test building a prompt with SpecBuilder."""
    builder = SpecBuilder()
    text_index = TextIndex(
        description="A text schema.",
        examples=["example1", "example2"],
    )
    mock_search_engine = MagicMock()
    mock_search_engine.model_fields = {"arguments": MagicMock(annotation=int)}
    builder.add("text_schema", text_index, mock_search_engine)
    prompt = builder.build_prompt("What is the schema?")
    prompt_expected_length = 2

    if len(prompt) != prompt_expected_length:
        msg = (
            f"Expected prompt length to be {prompt_expected_length}, "
            f"but got {len(prompt)}."
        )
        raise ValueError(msg)
    if prompt[0]["role"] != "system":
        msg = f"Expected first prompt role to be 'system', but got {prompt[0]['role']}."
        raise ValueError(msg)
    if "A text schema." not in prompt[0]["content"]:
        msg = "Expected 'A text schema.' to be in the first prompt content."
        raise ValueError(msg)
    if prompt[1]["role"] != "user":
        msg = f"Expected second prompt role to be 'user', but got {prompt[1]['role']}."
        raise ValueError(msg)
    if prompt[1]["content"] != "What is the schema?":
        msg = (
            "Expected second prompt content to be 'What is the schema?', "
            f"but got {prompt[1]['content']}."
        )
        raise ValueError(msg)


def test_spec_builder_build_format() -> None:
    """Test building a format with SpecBuilder."""
    builder = SpecBuilder()
    number_index = NumberIndex(
        description="A number schema.",
        range={"min": 0, "max": 100},
        examples=[10, 20, 30],
    )
    search_engine = TextSearchEngine(
        config=TextSearchEngineConfig(),
    )
    builder.add("number_schema", number_index, search_engine)
    format_model = builder.build_format()
    if "queries" not in format_model.model_fields:
        msg = "The model does not have the expected schema."
        raise ValueError(msg)
    query_list_type = format_model.model_fields["queries"].annotation
    if (
        not hasattr(query_list_type, "__origin__")
        and query_list_type.__origin__ is not list
    ):
        msg = "The queries field is not a list."
        raise TypeError(msg)
    if "number_schema" not in query_list_type.__args__[0].model_fields:
        msg = "The queries field does not contain the expected schema."
        raise ValueError(msg)


def test_spec_builder_empty_spec_error() -> None:
    """Test error when SpecBuilder has no schemas."""
    builder = SpecBuilder()
    with pytest.raises(ValueError, match="No schemas available to build a prompt."):
        builder.build_prompt("Test query")
    with pytest.raises(
        ValueError,
        match="No search engine schemas available to build a format.",
    ):
        builder.build_format()
    with pytest.raises(ValueError, match="No schemas available to query."):
        builder.query("Test query")


def test_spec_builder_empty_query_error() -> None:
    """Test error when query string is empty."""
    builder = SpecBuilder()
    text_index = TextIndex(
        description="A text schema.",
        examples=["example1", "example2"],
    )
    text_search_engine = TextSearchEngine(
        config=TextSearchEngineConfig(),
        arguments=TextSearchEngineArguments(keywords=["example"]),
    )

    builder.add("text_schema", text_index, text_search_engine)
    with pytest.raises(ValueError, match="Query string cannot be empty."):
        builder.query("")
