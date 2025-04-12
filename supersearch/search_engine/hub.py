"""Search engine registry."""

from supersearch.search_engine.base_engine import BaseSearchEngine

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

    def decorator(cls: BaseSearchEngine) -> type:
        if type_name in registered_search_engines:
            raise SearchEngineRegisterError(type_name)
        if not issubclass(cls, BaseSearchEngine):
            msg = f"{cls.__name__} must be a subclass of BaseSearchEngine."
            raise TypeError(msg)
        if cls.model_fields.get("config") is None:
            msg = f"{cls.__name__} must have a config attribute."
            raise AttributeError(msg)
        if cls.model_fields.get("arguments") is None:
            msg = f"{cls.__name__} must have an arguments attribute."
            raise AttributeError(msg)
        registered_search_engines[type_name] = cls
        return cls

    return decorator
