"""Worker."""

from pydantic import ValidationError

from supersearch.model.base import BaseModelClient
from supersearch.spec import Spec
from supersearch.spec.base_search_engine import BaseSearchResult


class Worker:
    """Worker class."""

    def __init__(self, spec: Spec, model_client: BaseModelClient) -> None:
        """Initialize the worker with spec."""
        self.spec = spec
        self.model_client = model_client

    def _build_messages(self, query: str) -> list[dict[str, str]]:
        """Build the prompt for the spec."""
        return [
            {
                "role": "system",
                "content": self.spec.prompt_message,
            },
            {
                "role": "user",
                "content": query,
            },
        ]

    def build_query(self, query: str) -> dict:
        """Generate the query based on the spec."""
        response = self.model_client.response(
            self._build_messages(query),
            self.spec.query_model,
        )

        try:
            self.spec.query_model(**response)
            return response["queries"]
        except KeyError:
            msg = "Failed to parse response: 'queries' key not found."
            raise ValueError(msg) from None
        except ValidationError as e:
            msg = f"Model didn't respond with a valid query: {e}"
            raise ValueError(msg) from e
        except Exception as e:
            msg = f"Unexpected error: {e}"
            raise ValueError(msg) from e

    def execute(self, query: str) -> list[dict[str, BaseSearchResult]]:
        """Execute the query."""
        search_queries = self.build_query(query)
        results = []
        for search_query in search_queries:
            result = {}
            for name, arguments in search_query.items():
                search_engine = self.spec.search_engine_spec[name]
                result[name] = search_engine.search(arguments)
            results.append(result)

        return results
