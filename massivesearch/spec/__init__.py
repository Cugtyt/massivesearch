"""Spec module."""

from massivesearch.spec.base_index import BaseIndex
from massivesearch.spec.base_search_engine import (
    BaseSearchEngine,
    BaseSearchEngineArguments,
    BaseSearchEngineConfig,
    BaseSearchResult,
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
