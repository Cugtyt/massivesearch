from unittest.mock import MagicMock, patch

import pytest
import yaml
from pydantic import BaseModel

from massivesearch.aggregator.base import BaseAggregator, BaseAggregatorResult
from massivesearch.index.base import BaseIndex
from massivesearch.model.base import BaseAIClient
from massivesearch.pipe.pipe import MassiveSearchPipe
from massivesearch.pipe.spec_index import SpecIndex
from massivesearch.search_engine.base import BaseSearchEngine, BaseSearchResultIndex


class MockIndex(BaseIndex):
    def prompt(self) -> str:  
        return "Mock Index Prompt"


class MockSearchEngineArgs(BaseModel):
    param1: str


class MockSearchEngine(BaseSearchEngine):
    def search(self, arguments: MockSearchEngineArgs) -> BaseSearchResultIndex:
        return BaseSearchResultIndex(results=[{"id": "1", "score": 1.0}])


class MockAggregator(BaseAggregator):
    def aggregate(
        self,
        results: list[dict[str, BaseSearchResultIndex]],
    ) -> BaseAggregatorResult:
        return BaseAggregatorResult(result="Aggregated")


class MockAIClient(BaseAIClient):
    def response(
        self,
        messages: list[dict[str, str]],
        format_model: type[BaseModel],
    ) -> dict:
        # Simulate a valid response structure based on a potential format_model
        return {
            "queries": [
                {"sub_query": "test sub query", "mock_index": {"param1": "value1"}},
            ],
        }


@pytest.fixture
def pipe():
    """Fixture for MassiveSearchPipe instance."""
    return MassiveSearchPipe()


@pytest.fixture
def registered_pipe(pipe):
    """Fixture for MassiveSearchPipe instance with registered types."""
    pipe.register_index_type("mock_index", MockIndex)
    pipe.register_search_engine_type("mock_engine", MockSearchEngine)
    pipe.register_aggregator_type("mock_aggregator", MockAggregator)
    pipe.register_ai_client_type("mock_ai", MockAIClient)
    return pipe


@pytest.fixture
def valid_spec():
    """Fixture for a valid spec dictionary."""
    return {
        "indexs": [
            {
                "name": "mock_index",
                "type": "mock_index",
                "description": "Test index",
                "search_engine": {
                    "type": "mock_engine",
                    "description": "Test engine",
                },
            },
        ],
        "aggregator": {"type": "mock_aggregator", "description": "Test aggregator"},
        "ai_client": {"type": "mock_ai", "description": "Test AI client"},
    }


@pytest.fixture
def built_pipe(registered_pipe, valid_spec):
    """Fixture for a built MassiveSearchPipe instance."""
    with patch("massivesearch.pipe.pipe.spec_validator") as mock_validator:
        registered_pipe.build(valid_spec)
        mock_validator.assert_called_once()
    return registered_pipe


# --- Test __init__ ---


def test_pipe_init_default(pipe):
    assert pipe.indexs == []
    assert pipe.aggregator is None
    assert pipe.ai_client is None
    assert pipe.registered_index_types == {}
    assert pipe.registered_search_engine_types == {}
    assert pipe.registered_aggregator_types == {}
    assert pipe.registered_ai_client_types == {}
    assert "{context}" in pipe.prompt_template
    assert pipe.prompt == ""
    assert pipe.format_model is None
    assert pipe.serach_query == []


def test_pipe_init_custom_prompt():
    template = "Custom template with {context}"
    pipe = MassiveSearchPipe(prompt_template=template)
    assert pipe.prompt_template == template


def test_pipe_init_invalid_prompt():
    with pytest.raises(
        ValueError,
        match="Prompt template must contain '{context}' placeholder.",
    ):
        MassiveSearchPipe(prompt_template="Invalid template")


# --- Test build_from_file ---


def test_build_from_file_success(pipe, tmp_path, valid_spec):
    filepath = tmp_path / "spec.yaml"
    with open(filepath, "w") as f:
        yaml.dump(valid_spec, f)

    with patch.object(pipe, "build") as mock_build:
        pipe.build_from_file(str(filepath))
        mock_build.assert_called_once_with(valid_spec)


def test_build_from_file_not_found(pipe, tmp_path):
    filepath = tmp_path / "non_existent.yaml"
    with pytest.raises(
        FileNotFoundError,
        match=f"File path '{filepath!s}' does not exist.",
    ):
        pipe.build_from_file(str(filepath))


def test_build_from_file_is_dir(pipe, tmp_path):
    dirpath = tmp_path / "spec_dir"
    dirpath.mkdir()
    with pytest.raises(ValueError, match=f"File path '{dirpath!s}' is not a file."):
        pipe.build_from_file(str(dirpath))


def test_build_from_file_not_yaml(pipe, tmp_path):
    filepath = tmp_path / "spec.txt"
    filepath.touch()
    with pytest.raises(
        ValueError,
        match=f"File path '{filepath!s}' is not a YAML file.",
    ):
        pipe.build_from_file(str(filepath))


def test_build_from_file_empty_path(pipe):
    with pytest.raises(ValueError, match="File path is required."):
        pipe.build_from_file("")


# --- Test build ---


def test_build_success(registered_pipe, valid_spec):
    with (
        patch("massivesearch.pipe.pipe.spec_validator") as mock_validator,
        patch.object(registered_pipe, "_build_prompt") as mock_build_prompt,
        patch.object(registered_pipe, "_build_format_model") as mock_build_format_model,
        patch.object(
            registered_pipe,
            "_get_arguments_type",
            return_value=MockSearchEngineArgs,
        ) as mock_get_args,
    ):
        registered_pipe.build(valid_spec)

        mock_validator.assert_called_once()
        assert len(registered_pipe.indexs) == 1
        assert isinstance(registered_pipe.indexs[0], SpecIndex)
        assert registered_pipe.indexs[0].name == "mock_index"
        assert isinstance(registered_pipe.indexs[0].index, MockIndex)
        assert isinstance(registered_pipe.indexs[0].search_engine, MockSearchEngine)
        assert (
            registered_pipe.indexs[0].search_engine_arguments_type
            == MockSearchEngineArgs
        )
        assert isinstance(registered_pipe.aggregator, MockAggregator)
        assert isinstance(registered_pipe.ai_client, MockAIClient)
        mock_get_args.assert_called_once()
        mock_build_prompt.assert_called_once()
        mock_build_format_model.assert_called_once()


def test_build_no_spec(pipe):
    with pytest.raises(ValueError, match="No schemas available to build."):
        pipe.build(None)
    with pytest.raises(ValueError, match="No schemas available to build."):
        pipe.build({})


def test_build_validation_error(registered_pipe, valid_spec):
    with patch(
        "massivesearch.pipe.pipe.spec_validator",
        side_effect=ValueError("Validation failed"),
    ) as mock_validator:
        with pytest.raises(ValueError, match="Validation failed"):
            registered_pipe.build(valid_spec)
        mock_validator.assert_called_once()


# --- Test _build_prompt ---


def test_build_prompt_success(built_pipe):
    # build() calls _build_prompt, so we check the result on a built pipe
    assert built_pipe.prompt != ""
    assert "{context}" not in built_pipe.prompt  # Placeholder should be replaced
    assert "Mock Index Prompt" in built_pipe.prompt  # Content from mock index


def test_build_prompt_not_built(pipe):
    with pytest.raises(
        ValueError,
        match="Spec is not fully built. Cannot build prompt.",
    ):
        pipe._build_prompt()


# --- Test _build_format_model ---


def test_build_format_model_success(built_pipe):
    # build() calls _build_format_model, check result on built pipe
    assert built_pipe.format_model is not None
    assert issubclass(built_pipe.format_model, BaseModel)
    assert "queries" in built_pipe.format_model.model_fields
    # Check the structure of the inner model
    inner_model = built_pipe.format_model.model_fields["queries"].annotation.__args__[0]
    assert "sub_query" in inner_model.model_fields
    assert "mock_index" in inner_model.model_fields
    assert inner_model.model_fields["mock_index"].annotation == MockSearchEngineArgs


def test_build_format_model_not_built(pipe):
    with pytest.raises(
        ValueError,
        match="Spec is not fully built. Cannot build format model.",
    ):
        pipe._build_format_model()


# --- Test _get_arguments_type ---


def test_get_arguments_type_success(pipe):
    args_type = pipe._get_arguments_type(MockSearchEngine())
    assert args_type == MockSearchEngineArgs


def test_get_arguments_type_no_search_engine(pipe):
    with pytest.raises(
        ValueError,
        match="No search engine available to get arguments type.",
    ):
        pipe._get_arguments_type(None)


def test_get_arguments_type_no_arguments_param(pipe):
    class NoArgsEngine(BaseSearchEngine):
        def search(self, other_param: str) -> BaseSearchResultIndex:
            pass

    with pytest.raises(
        ValueError,
        match="'arguments' parameter not found in search function.",
    ):
        pipe._get_arguments_type(NoArgsEngine())


def test_get_arguments_type_no_annotation(pipe):
    class NoAnnotationEngine(BaseSearchEngine):
        def search(self, arguments) -> BaseSearchResultIndex:
            pass  # No type hint

    with pytest.raises(ValueError, match="'arguments' parameter has no annotation."):
        pipe._get_arguments_type(NoAnnotationEngine())


# --- Test Registration ---


def test_register_index_type_success(pipe):
    pipe.register_index_type("test_index", MockIndex)
    assert "test_index" in pipe.registered_index_types
    assert pipe.registered_index_types["test_index"] == MockIndex


def test_register_search_engine_type_success(pipe):
    pipe.register_search_engine_type("test_engine", MockSearchEngine)
    assert "test_engine" in pipe.registered_search_engine_types
    assert pipe.registered_search_engine_types["test_engine"] == MockSearchEngine


def test_register_aggregator_type_success(pipe):
    pipe.register_aggregator_type("test_aggregator", MockAggregator)
    assert "test_aggregator" in pipe.registered_aggregator_types
    assert pipe.registered_aggregator_types["test_aggregator"] == MockAggregator


def test_register_ai_client_type_success(pipe):
    pipe.register_ai_client_type("test_ai", MockAIClient)
    assert "test_ai" in pipe.registered_ai_client_types
    assert pipe.registered_ai_client_types["test_ai"] == MockAIClient


def test_register_type_decorator(pipe):
    @pipe.index_type("decorated_index")
    class DecoratedIndex(MockIndex):
        pass

    @pipe.search_engine_type("decorated_engine")
    class DecoratedEngine(MockSearchEngine):
        pass

    @pipe.aggregator_type("decorated_aggregator")
    class DecoratedAggregator(MockAggregator):
        pass

    @pipe.ai_client_type("decorated_ai")
    class DecoratedAI(MockAIClient):
        pass

    assert "decorated_index" in pipe.registered_index_types
    assert pipe.registered_index_types["decorated_index"] == DecoratedIndex
    assert "decorated_engine" in pipe.registered_search_engine_types
    assert pipe.registered_search_engine_types["decorated_engine"] == DecoratedEngine
    assert "decorated_aggregator" in pipe.registered_aggregator_types
    assert (
        pipe.registered_aggregator_types["decorated_aggregator"] == DecoratedAggregator
    )
    assert "decorated_ai" in pipe.registered_ai_client_types
    assert pipe.registered_ai_client_types["decorated_ai"] == DecoratedAI


def test_register_type_no_name(pipe):
    with pytest.raises(ValueError, match="Name is required."):
        pipe.register_index_type("", MockIndex)


def test_register_type_wrong_base_class(pipe):
    class WrongClass:
        pass

    with pytest.raises(
        TypeError,
        match="Class 'WrongClass' is not a subclass of BaseIndex.",
    ):
        pipe.register_index_type("wrong", WrongClass)


def test_register_type_duplicate_name(pipe):
    pipe.register_index_type("duplicate", MockIndex)
    with pytest.raises(
        ValueError,
        match="Index with name 'duplicate' is already registered.",
    ):
        pipe.register_index_type("duplicate", MockIndex)


# --- Test __or__ ---


def test_or_success():
    pipe1 = MassiveSearchPipe()
    pipe2 = MassiveSearchPipe()

    class Index1(MockIndex):
        pass

    class Engine1(MockSearchEngine):
        pass

    class Index2(MockIndex):
        pass

    class Engine2(MockSearchEngine):
        pass

    pipe1.register_index_type("index1", Index1)
    pipe1.register_search_engine_type("engine1", Engine1)
    pipe2.register_index_type("index2", Index2)
    pipe2.register_search_engine_type("engine2", Engine2)

    combined = pipe1 | pipe2

    assert isinstance(combined, MassiveSearchPipe)
    assert "index1" in combined.registered_index_types
    assert "engine1" in combined.registered_search_engine_types
    assert "index2" in combined.registered_index_types
    assert "engine2" in combined.registered_search_engine_types
    assert combined.aggregator is None
    assert combined.ai_client is None


def test_or_type_error():
    pipe1 = MassiveSearchPipe()
    with pytest.raises(
        TypeError,
        match="Can only combine with another MassiveSearchPipe instance.",
    ):
        _ = pipe1 | "not a pipe"


def test_or_aggregator_set():
    pipe1 = MassiveSearchPipe()
    pipe2 = MassiveSearchPipe()
    pipe1.aggregator = MockAggregator()  # Set aggregator on pipe1
    with pytest.raises(ValueError, match="Aggregator already set"):
        _ = pipe1 | pipe2

    pipe1.aggregator = None
    pipe2.aggregator = MockAggregator()  # Set aggregator on pipe2
    with pytest.raises(ValueError, match="Aggregator already set"):
        _ = pipe1 | pipe2


def test_or_ai_client_set():
    pipe1 = MassiveSearchPipe()
    pipe2 = MassiveSearchPipe()
    pipe1.ai_client = MockAIClient()  # Set AI client on pipe1
    with pytest.raises(ValueError, match="AI client already set"):
        _ = pipe1 | pipe2

    pipe1.ai_client = None
    pipe2.ai_client = MockAIClient()  # Set AI client on pipe2
    with pytest.raises(ValueError, match="AI client already set"):
        _ = pipe1 | pipe2


def test_or_type_overlap():
    pipe1 = MassiveSearchPipe()
    pipe2 = MassiveSearchPipe()
    pipe1.register_index_type("overlap_index", MockIndex)
    pipe2.register_index_type("overlap_index", MockIndex)  # Same name
    with pytest.raises(ValueError, match="Index types overlap: {'overlap_index'}"):
        _ = pipe1 | pipe2


# --- Test _build_messages ---


def test_build_messages(built_pipe):
    query = "test query"
    built_pipe.prompt = "System prompt"  # Set manually for simplicity
    messages = built_pipe._build_messages(query)
    assert messages == [
        {"role": "system", "content": "System prompt"},
        {"role": "user", "content": query},
    ]


# --- Test build_query ---


def test_build_query_success(built_pipe):
    query = "user query"
    mock_response = {
        "queries": [
            {"sub_query": "ai sub query", "mock_index": {"param1": "ai_value"}},
        ],
    }

    # Mock the AI client's response
    built_pipe.ai_client.response = MagicMock(return_value=mock_response)
    # Mock _build_messages
    with patch.object(
        built_pipe,
        "_build_messages",
        return_value=[{"role": "user", "content": query}],
    ) as mock_build_msg:
        result = built_pipe.build_query(query)

        mock_build_msg.assert_called_once_with(query)
        built_pipe.ai_client.response.assert_called_once_with(
            mock_build_msg.return_value,
            built_pipe.format_model,
        )
        assert result == mock_response["queries"]
        assert built_pipe.serach_query == mock_response["queries"]


def test_build_query_missing_key(built_pipe):
    query = "user query"
    mock_response = {"wrong_key": []}  # Missing 'queries'
    built_pipe.ai_client.response = MagicMock(return_value=mock_response)

    with pytest.raises(
        ValueError,
        match="Failed to parse response: 'queries' key not found.",
    ):
        built_pipe.build_query(query)


def test_build_query_validation_error(built_pipe):
    query = "user query"
    # Response structure doesn't match format_model (e.g., missing sub_query)
    mock_response = {"queries": [{"mock_index": {"param1": "value"}}]}
    built_pipe.ai_client.response = MagicMock(return_value=mock_response)

    with pytest.raises(ValueError, match="Model didn't respond with a valid query"):
        built_pipe.build_query(query)


def test_build_query_ai_client_exception(built_pipe):
    query = "user query"
    built_pipe.ai_client.response = MagicMock(side_effect=Exception("AI Error"))

    with pytest.raises(ValueError, match="Unexpected error: AI Error"):
        built_pipe.build_query(query)


# --- Test search ---


def test_search_success(built_pipe):
    query = "search query"
    mock_search_queries = [{"sub_query": "sub1", "mock_index": {"param1": "val1"}}]
    mock_search_result = BaseSearchResultIndex(results=[{"id": "res1", "score": 0.9}])

    # Mock build_query
    with (
        patch.object(
            built_pipe,
            "build_query",
            return_value=mock_search_queries,
        ) as mock_build,
        patch.object(
            built_pipe.indexs[0].search_engine,
            "search",
            return_value=mock_search_result,
        ) as mock_search,
    ):
        results = built_pipe.search(query)

        mock_build.assert_called_once_with(query)
        # Assert search was called with correctly parsed arguments
        mock_search.assert_called_once()
        call_args = mock_search.call_args[0][0]
        assert isinstance(call_args, MockSearchEngineArgs)
        assert call_args.param1 == "val1"

        assert len(results) == 1
        assert "mock_index" in results[0]
        assert results[0]["mock_index"] == mock_search_result


# --- Test run ---


def test_run_success(built_pipe):
    query = "run query"
    mock_search_results = [{"mock_index": BaseSearchResultIndex(results=[])}]
    mock_agg_result = BaseAggregatorResult(result="Final Answer")

    # Mock search method
    with (
        patch.object(
            built_pipe,
            "search",
            return_value=mock_search_results,
        ) as mock_search,
        patch.object(
            built_pipe.aggregator,
            "aggregate",
            return_value=mock_agg_result,
        ) as mock_aggregate,
    ):
        final_result = built_pipe.run(query)

        mock_search.assert_called_once_with(query)
        mock_aggregate.assert_called_once_with(mock_search_results)
        assert final_result == mock_agg_result
