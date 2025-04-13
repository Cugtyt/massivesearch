"""Index module."""

from supersearch.index.base import BaseIndex
from supersearch.index.bool import BoolIndex
from supersearch.index.date import DateIndex
from supersearch.index.hub import index, registered_indexs
from supersearch.index.number import NumberIndex
from supersearch.index.text import TextIndex
from supersearch.index.vector import VectorIndex

__all__ = [
    "BaseIndex",
    "BoolIndex",
    "DateIndex",
    "NumberIndex",
    "TextIndex",
    "VectorIndex",
    "index",
    "registered_indexs",
]
