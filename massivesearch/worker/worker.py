"""Worker."""

from pydantic import ValidationError

from massivesearch.aggregator import Aggregator, AggregatorResult
from massivesearch.model.base import BaseModelClient
from massivesearch.search_engine.base import BaseSearchResultIndex
from massivesearch.spec import Spec

WorkerSearchResult = list[dict[str, BaseSearchResultIndex]]


class Worker:
    """Worker class."""

    def __init__(
        self,
        spec: Spec,
        model_client: BaseModelClient,
        aggregator: Aggregator,
    ) -> None:
        """Initialize the worker with spec."""
        self.spec = spec
        self.model_client = model_client
        self.last_search_query: list[dict] = []
        self.aggregator = aggregator

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

    def build_query(self, query: str) -> list[dict]:
        """Generate the query based on the spec."""
        response = self.model_client.response(
            self._build_messages(query),
            self.spec.query_model,
        )

        try:
            self.spec.query_model(**response)
            self.last_search_query = response["queries"]
            return self.last_search_query
        except KeyError:
            msg = "Failed to parse response: 'queries' key not found."
            raise ValueError(msg) from None
        except ValidationError as e:
            msg = f"Model didn't respond with a valid query: {e}"
            raise ValueError(msg) from e
        except Exception as e:
            msg = f"Unexpected error: {e}"
            raise ValueError(msg) from e

    def search(self, query: str) -> WorkerSearchResult:
        """Execute the query."""
        search_queries = self.build_query(query)
        execute_results = []
        for search_query in search_queries:
            result = {}
            for name, spec_unit in self.spec.items.items():
                search_engine_arguments = spec_unit.search_engine_arguments_type(
                    **search_query[name],
                )
                search_result = spec_unit.search_engine.search(
                    search_engine_arguments,
                )
                result[name] = search_result
            execute_results.append(result)

        return execute_results

    def execute(self, query: str) -> AggregatorResult:
        """Execute the query."""
        search_results = self.search(query)
        return self.aggregator.aggregate(self.search(query))
