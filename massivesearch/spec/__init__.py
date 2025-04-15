"""Spec module."""

from massivesearch.index.base import BaseIndex
from massivesearch.search_engine.base import (
    BaseSearchEngine,
    BaseSearchEngineArguments,
    BaseSearchResultIndex,
)
from massivesearch.spec.builder import SpecBuilder
from massivesearch.spec.spec import Spec, SpecIndexUnit
from massivesearch.spec.validator import (
    SpecSchemaError,
    spec_validator,
)

__all__ = [
    "BaseIndex",
    "BaseSearchEngine",
    "BaseSearchEngineArguments",
    "BaseSearchResultIndex",
    "Spec",
    "SpecBuilder",
    "SpecIndexUnit",
    "SpecSchemaError",
    "SpecValidationError",
    "SpecValidationError",
    "spec_validator",
]
