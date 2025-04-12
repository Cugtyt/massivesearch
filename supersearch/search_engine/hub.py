"""Search engine registry."""

registered_search_engines = {}


class SearchEngineRegisterError(Exception):
    """Custom exception for search enginee registration errors."""

    def __init__(self, type_name: str) -> None:
        """Initialize the exception with a type name."""
        super().__init__(
            f"Search engine with type name '{type_name}' is already registered.",
        )


def search_engine(type_name: str) -> callable:
    """Register a search engine with a given key name."""

    def decorator(cls: type) -> type:
        if type_name in registered_search_engines:
            raise SearchEngineRegisterError(type_name)
        registered_search_engines[type_name] = cls
        return cls

    return decorator
