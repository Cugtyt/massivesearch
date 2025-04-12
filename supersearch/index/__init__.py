"""Index module."""

from supersearch.index.schema.base import BaseIndexSchema
from supersearch.index.schema.bool import BoolIndexSchema
from supersearch.index.schema.date import DateIndexSchema
from supersearch.index.schema.hub import index_schema, registered_schemas
from supersearch.index.schema.number import NumberIndexSchema
from supersearch.index.schema.text import TextIndexSchema
from supersearch.index.schema.vector import VectorIndexSchema

__all__ = [
    "BaseIndexSchema",
    "BoolIndexSchema",
    "DateIndexSchema",
    "NumberIndexSchema",
    "SchemaTypeError",
    "SchemaValidationError",
    "TextIndexSchema",
    "VectorIndexSchema",
    "index_schema",
    "registered_schemas",
]
