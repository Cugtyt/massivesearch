"""Yaml file validator for index schema types."""

from pydantic import ValidationError

from supersearch.index.schema.hub import registered_schemas


class SchemaTypeError(Exception):
    """Custom exception for schema type errors."""

    def __init__(self, index_name: str, type_name: str) -> None:
        """Initialize the exception with a type name."""
        super().__init__(
            f"Index '{index_name}' schema with type name '{type_name}' is unknown.",
        )


class SchemaValidationError(Exception):
    """Custom exception for schema validation errors."""

    def __init__(self, errors: dict) -> None:
        """Initialize the exception with a schema type and errors."""
        super().__init__(f"Schema validation errors: {errors}")


def yaml_validator(yaml: dict) -> None:
    """Validate the yaml for index schema types."""
    validation_errors = {}
    for index_name, schema in yaml.items():
        type_name = schema.get("type")
        if type_name not in registered_schemas:
            raise SchemaTypeError(index_name, type_name)
        try:
            registered_schemas[type_name](**schema)
        except ValidationError as e:
            validation_errors[index_name] = str(e)

    if validation_errors:
        raise SchemaValidationError(validation_errors)
