"""Base class for search engines."""

from abc import abstractmethod
from types import NoneType
from typing import Any, Generic, TypeVar, get_args, get_origin

from pydantic import BaseModel, ConfigDict
from pydantic.fields import FieldInfo

SearchArgT = TypeVar("SearchArgT", bound=BaseModel)


SearchResT = TypeVar("SearchResT")


class BaseSearchEngine(BaseModel, Generic[SearchArgT, SearchResT]):
    """Base class for search engines."""

    model_config = ConfigDict(extra="ignore")

    @staticmethod
    def _format_field_header(name: str, field_info: FieldInfo, indent: str) -> str:
        """Format the header part of a field description."""
        field_line = f"{indent}{name}"
        if field_info.description:
            field_line += f": {field_info.description}"
        if field_info.examples:
            safe_examples = [str(ex) for ex in field_info.examples]
            field_line += f" (examples: {', '.join(safe_examples)})"
        return field_line

    @classmethod
    def _process_single_arg(
        cls,
        arg: Any,  # noqa: ANN401
        indent: str,
        processed_models: set[type[BaseModel]],
    ) -> tuple[str, list[str]]:
        """Process a single argument (e.g., within a generic type)."""
        nested_details = []
        if arg is NoneType:
            arg_str = "None"
        elif isinstance(arg, type) and issubclass(arg, BaseModel):
            arg_str = arg.__name__
            # Recursively generate prompt for nested model if not already processed
            if arg not in processed_models:
                processed_models.add(arg)  # Mark before recursing
                nested_prompt = cls._generate_model_prompt_recursive(
                    arg,
                    indent * 2,
                    processed_models,
                )
                if nested_prompt:
                    nested_details.append(
                        f"{indent * 2}Details for {arg_str}:\n{indent}{nested_prompt}",
                    )
        elif isinstance(arg, type):
            arg_str = arg.__name__
        else:
            arg_str = str(arg)  # Handle TypeVars, literals, etc.
        return arg_str, nested_details

    @classmethod
    def _process_annotation(
        cls,
        annotation: Any,  # noqa: ANN401
        indent: str,
        processed_models: set[type[BaseModel]],
    ) -> tuple[str, list[str]]:
        """Process annotation to get string representation and nested details."""
        origin = get_origin(annotation)
        args = get_args(annotation)
        nested_details_list = []
        type_str_part = ""

        if origin:  # Generic types like list[T], dict[K, V], Union[T, U]
            origin_name = getattr(origin, "__name__", str(origin))
            arg_strs = []
            for arg in args:
                arg_str, nested_details = cls._process_single_arg(
                    arg,
                    indent,
                    processed_models,
                )
                arg_strs.append(arg_str)
                nested_details_list.extend(nested_details)
            type_str_part = f"type: {origin_name}[{', '.join(arg_strs)}]"

        elif isinstance(annotation, type) and issubclass(
            annotation,
            BaseModel,
        ):  # Direct BaseModel subclass
            type_name = annotation.__name__
            type_str_part = f"type: {type_name}"
            # Recursively generate prompt for nested model if not already processed
            if annotation not in processed_models:
                processed_models.add(annotation)  # Mark before recursing
                nested_prompt = cls._generate_model_prompt_recursive(
                    annotation,
                    indent * 2,
                    processed_models,
                )
                if nested_prompt:
                    nested_details_list.append(
                        (
                            f"{indent * 2}Details for {type_name}:\n"
                            f"{indent}{nested_prompt}"
                        ),
                    )

        elif isinstance(annotation, type):  # Other simple types
            type_str_part = f"type: {annotation.__name__}"
        # else: could handle other annotation types if needed

        return type_str_part, nested_details_list

    @classmethod
    def _generate_model_prompt_recursive(
        cls,
        model: type[BaseModel],
        indent: str,
        processed_models: set[type[BaseModel]],
    ) -> str:
        """Generate prompt string for a Pydantic model, handling nesting recursively."""
        prompt_lines = []

        for name, field_info in model.model_fields.items():
            # Format the basic field info line
            field_line = cls._format_field_header(name, field_info, indent)

            # Process the type annotation to get type string and nested details
            type_str_part, nested_details = cls._process_annotation(
                field_info.annotation,
                indent,
                processed_models,
            )

            # Append type string if available
            if type_str_part:
                field_line += f" ({type_str_part})"

            prompt_lines.append(field_line)
            # Append details generated from nested models within this field's annotation
            prompt_lines.extend(nested_details)

        return "\n".join(prompt_lines)

    @classmethod
    def prompt(cls) -> str:
        """Return the prompt for the search engine, including nested models."""
        arguments_annotation = cls.search.__annotations__["arguments"]

        # Use the recursive helper to generate the prompt
        processed_models: set[type[BaseModel]] = (
            set()
        )  # Track processed models for this call
        params_prompt = cls._generate_model_prompt_recursive(
            arguments_annotation,
            "  ",
            processed_models,
        )

        if not params_prompt:
            return (
                "Search Engine Parameters: Not needed."  # Or Arguments model is empty
            )
        return "Search Engine Parameters:\n" + params_prompt

    @abstractmethod
    async def search(
        self,
        arguments: SearchArgT,
    ) -> SearchResT:
        """Search for the given arguments."""
