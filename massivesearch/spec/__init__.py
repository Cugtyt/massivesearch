"""Spec module."""

from massivesearch.index.base import BaseIndex
from massivesearch.search_engine.base import (
    BaseSearchEngine,
    BaseSearchEngineArguments,
    BaseSearchEngineConfig,
    BaseSearchResultIndex,
)
from massivesearch.spec.builder import SpecBuilder
from massivesearch.spec.spec import Spec, SpecUnit
from massivesearch.spec.validator import (
    SpecIndexTypeError,
    SpecSearchEngineError,
    SpecValidationError,
    spec_validator,
)

__all__ = [
    "BaseIndex",
    "BaseSearchEngine",
    "BaseSearchEngineArguments",
    "BaseSearchEngineConfig",
    "BaseSearchResultIndex",
    "Spec",
    "SpecBuilder",
    "SpecIndexTypeError",
    "SpecIndexTypeError",
    "SpecSearchEngineError",
    "SpecUnit",
    "SpecValidationError",
    "SpecValidationError",
    "spec_validator",
]
