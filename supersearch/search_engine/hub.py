"""Search engine registry."""

from supersearch.search_engine.base_engine import (
    BaseSearchEngine,
    BaseSearchEngineArguments,
    BaseSearchEngineConfig,
    BaseSearchResult,
)

registered_search_engines: dict[str, type[BaseSearchEngine]] = {}


class SearchEngineRegisterError(Exception):
    """Custom exception for search enginee registration errors."""

    def __init__(self, type_name: str) -> None:
        """Initialize the exception with a type name."""
        super().__init__(
            f"Search engine with type name '{type_name}' is already registered.",
        )


def search_engine(name: str) -> type[BaseSearchEngine]:
    """Register a search engine with a given key name."""

    def validate_search_engine(cls: type[BaseSearchEngine]) -> None:
        _validate_registration(name, cls)
        _validate_config(cls)
        _validate_search_method(cls)

    def decorator(cls: type[BaseSearchEngine]) -> type:
        validate_search_engine(cls)
        registered_search_engines[name] = cls
        return cls

    return decorator


def _validate_registration(type_name: str, cls: type[BaseSearchEngine]) -> None:
    if type_name in registered_search_engines:
        raise SearchEngineRegisterError(type_name)
    if not issubclass(cls, BaseSearchEngine):
        msg = f"{cls.__name__} must be a subclass of BaseSearchEngine."
        raise TypeError(msg)


def _validate_config(cls: type[BaseSearchEngine]) -> None:
    if cls.model_fields.get("config") is None:
        msg = f"{cls.__name__} must have a config attribute."
        raise AttributeError(msg)
    if not issubclass(
        cls.model_fields.get("config").annotation,
        BaseSearchEngineConfig,
    ):
        msg = f"{cls.__name__} config must be a subclass of BaseSearchEngineConfig."
        raise TypeError(msg)


def _validate_search_method(cls: type[BaseSearchEngine]) -> None:
    if hasattr(cls, "search") and not callable(cls.search):
        msg = f"{cls.__name__} must have a callable search method."
        raise AttributeError(msg)
    if cls.search.__annotations__.get("arguments") is None:
        msg = f"{cls.__name__} search method must have an arguments attribute."
        raise AttributeError(msg)
    arguments_annotation = cls.search.__annotations__.get("arguments")
    if not issubclass(arguments_annotation, BaseSearchEngineArguments):
        msg = (
            f"{cls.__name__} search method arguments must be a "
            f"subclass of BaseSearchEngineArguments."
        )
        raise TypeError(msg)
    if cls.search.__annotations__.get("return") is None:
        msg = f"{cls.__name__} search method must have a return type."
        raise AttributeError(msg)
    return_annotation = cls.search.__annotations__.get("return")
    if not issubclass(return_annotation, BaseSearchResult):
        msg = (
            f"{cls.__name__} search method return type must be a "
            f"subclass of BaseSearchResult."
        )
        raise TypeError(msg)
