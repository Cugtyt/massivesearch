"""Spec module."""

from supersearch.spec.base_index import BaseIndex
from supersearch.spec.base_search_engine import (
    BaseSearchEngine,
    BaseSearchEngineArguments,
    BaseSearchEngineConfig,
    BaseSearchResult,
)
from supersearch.spec.builder import SpecBuilder
from supersearch.spec.spec import Spec, SpecUnit
from supersearch.spec.validator import (
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
    "BaseSearchResult",
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
