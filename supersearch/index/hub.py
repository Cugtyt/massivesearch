"""Schema registry."""

from supersearch.index.base import BaseIndex

registered_indexs: dict[str, type[BaseIndex]] = {}


class SchemaRegisterError(Exception):
    """Custom exception for schema registration errors."""

    def __init__(self, type_name: str) -> None:
        """Initialize the exception with a type name."""
        super().__init__(f"Schema with type name '{type_name}' is already registered.")


def index(name: str) -> type[BaseIndex]:
    """Register a schema with a given key name."""

    def decorator(cls: type[BaseIndex]) -> type[BaseIndex]:
        if name in registered_indexs:
            raise SchemaRegisterError(cls.type)
        registered_indexs[name] = cls

        return cls

    return decorator
