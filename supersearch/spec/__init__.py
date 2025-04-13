"""Spec module."""

from supersearch.spec.builder import SpecBuilder
from supersearch.spec.spec import Spec
from supersearch.spec.validator import spec_validator

__all__ = [
    "Spec",
    "SpecBuilder",
    "spec_validator",
]
