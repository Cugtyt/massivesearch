"""Schema registry."""

registered_schemas = {}


class SchemaRegisterError(Exception):
    """Custom exception for schema registration errors."""

    def __init__(self, type_name: str) -> None:
        """Initialize the exception with a type name."""
        super().__init__(f"Schema with type name '{type_name}' is already registered.")


def index_schema(type_name: str) -> callable:
    """Register a schema with a given key name."""

    def decorator(cls: type) -> type:
        if type_name in registered_schemas:
            raise SchemaRegisterError(type_name)
        registered_schemas[type_name] = cls
        return cls

    return decorator
