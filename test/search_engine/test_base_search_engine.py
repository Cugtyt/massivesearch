from types import NoneType
from typing import Any

import pytest
from pydantic import BaseModel, Field
from pydantic.fields import FieldInfo

from massivesearch.search_engine.base import BaseSearchEngine

# ruff: noqa: D100, D101, D102, ARG001, D103, S101, SLF001, D107, ANN001, ANN201, PGH003


# --- Mock Models ---
class SimpleArgs(BaseModel):
    """Simple arguments model."""

    query: str = Field(description="The search query.")
    limit: int = Field(10, description="Maximum results.", examples=[5, 10])


class InnerModel(BaseModel):
    """An inner model for nesting."""

    inner_field: bool = Field(description="An inner boolean field.")


class NestedArgs(BaseModel):
    """Arguments model with nesting."""

    outer_field: str = Field(description="Outer string field.")
    nested: InnerModel = Field(description="A nested model instance.")
    optional_nested: InnerModel | None = Field(
        None,
        description="Optional nested model.",
    )
    list_nested: list[InnerModel] = Field(
        default_factory=list,
        description="List of nested models.",
    )


class ComplexArgs(BaseModel):
    """Arguments model with complex types."""

    name: str
    tags: list[str] = Field(description="List of tags.")
    metadata: dict[str, NoneType] = Field(description="Arbitrary metadata.")
    union_field: int | str = Field(description="Can be int or str.")
    optional_field: float | None = Field(None, description="An optional float.")
    none_type_field: NoneType = Field(None, description="A field that is None.")


class EmptyArgs(BaseModel):
    """An empty arguments model."""


class MockReturnType:
    """A mock return type for search engines."""


# --- Mock Search Engines ---
class SimpleSearchEngine(BaseSearchEngine[SimpleArgs, None]):
    """Search engine using SimpleArgs."""

    async def search(self, arguments: SimpleArgs) -> None:
        pass


class NestedSearchEngine(BaseSearchEngine[NestedArgs, None]):
    """Search engine using NestedArgs."""

    async def search(self, arguments: NestedArgs) -> None:
        pass


class ComplexSearchEngine(BaseSearchEngine[ComplexArgs, None]):
    """Search engine using ComplexArgs."""

    async def search(self, arguments: ComplexArgs) -> None:
        pass


class EmptySearchEngine(BaseSearchEngine[EmptyArgs, None]):
    """Search engine using EmptyArgs."""

    async def search(self, arguments: EmptyArgs) -> None:
        pass


class NoArgumentsParamSearchEngine(BaseSearchEngine):
    """Search engine whose search method lacks 'arguments' parameter."""

    async def search(self, query: str) -> None:  # type: ignore
        pass


class NonBaseModelArgSearchEngine(BaseSearchEngine):
    """Search engine where 'arguments' is not a BaseModel."""

    async def search(self, arguments: str) -> None:
        pass


# --- Test Cases ---


def test_prompt_simple_args() -> None:
    """Test prompt generation for SimpleArgs."""
    expected_prompt = """Search Engine Parameters:
  query: The search query. (type: str)
  limit: Maximum results. (examples: 5, 10) (type: int)"""
    assert SimpleSearchEngine.prompt() == expected_prompt


def test_prompt_nested_args() -> None:
    """Test prompt generation for NestedArgs, including nested details."""
    expected_prompt = """Search Engine Parameters:
  outer_field: Outer string field. (type: str)
  nested: A nested model instance. (type: InnerModel)
    Details for InnerModel:
      inner_field: An inner boolean field. (type: bool)
  optional_nested: Optional nested model. (type: UnionType[InnerModel, None])
  list_nested: List of nested models. (type: list[InnerModel])"""
    # Normalize whitespace for comparison as indentation can be tricky
    assert "\n".join(line.rstrip() for line in SimpleSearchEngine.prompt().splitlines())
    assert "\n".join(
        line.rstrip() for line in NestedSearchEngine.prompt().splitlines()
    ) == "\n".join(line.rstrip() for line in expected_prompt.splitlines())


def test_prompt_complex_args() -> None:
    """Test prompt generation for ComplexArgs."""
    expected_prompt = """Search Engine Parameters:
  name (type: str)
  tags: List of tags. (type: list[str])
  metadata: Arbitrary metadata. (type: dict[str, None])
  union_field: Can be int or str. (type: UnionType[int, str])
  optional_field: An optional float. (type: UnionType[float, None])
  none_type_field: A field that is None. (type: NoneType)"""
    assert ComplexSearchEngine.prompt() == expected_prompt


def test_prompt_empty_args() -> None:
    """Test prompt generation for an empty args model."""
    expected_prompt = "Search Engine Parameters: Not needed."
    assert EmptySearchEngine.prompt() == expected_prompt


def test_prompt_no_arguments_parameter() -> None:
    """Test prompt generation when 'search' lacks 'arguments' parameter."""
    with pytest.raises(
        KeyError,
        match="'arguments'",
    ):  # Expecting KeyError when accessing __annotations__
        NoArgumentsParamSearchEngine.prompt()


def test_prompt_non_basemodel_argument() -> None:
    """Test prompt generation when 'arguments' is not a BaseModel subclass."""
    with pytest.raises(
        AttributeError,
        match="type object 'str' has no attribute 'model_fields'",
    ):
        NonBaseModelArgSearchEngine.prompt()


def test_format_field_header() -> None:
    """Test the _format_field_header helper method."""
    # Basic name
    assert (
        BaseSearchEngine._format_field_header(
            "field1",
            FieldInfo(),
            "",
        )
        == "field1"
    )
    # Name and description
    assert (
        BaseSearchEngine._format_field_header(
            "field2",
            FieldInfo(description="Desc"),
            "\t",
        )
        == "\tfield2: Desc"
    )
    # Name and examples
    assert (
        BaseSearchEngine._format_field_header(
            "field3",
            FieldInfo(examples=["ex1", 2]),
            "",
        )
        == "field3 (examples: ex1, 2)"
    )
    # Name, description, and examples
    assert (
        BaseSearchEngine._format_field_header(
            "field4",
            FieldInfo(description="Desc 4", examples=[True]),
            "  ",
        )
        == "  field4: Desc 4 (examples: True)"
    )
