"""Index Test."""

from test.index.bool import spec_builder as bool_index_spec_builder
from test.index.date import spec_builder as date_index_spec_builder
from test.index.number import spec_builder as number_index_spec_builder
from test.index.text import spec_builder as text_index_spec_builder
from test.index.vector import spec_builder as vector_index_spec_builder

__all__ = [
    "bool_index_spec_builder",
    "date_index_spec_builder",
    "number_index_spec_builder",
    "text_index_spec_builder",
    "vector_index_spec_builder",
]
