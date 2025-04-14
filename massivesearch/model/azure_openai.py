"""Model module."""

import json
from typing import Self

from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from openai import AzureOpenAI

from massivesearch.model.base import BaseModelClient


class AzureOpenAIClient(BaseModelClient):
    """A client wrapper for interacting with the Azure OpenAI service."""

    def __init__(self, **kwargs: dict[str, str]) -> Self:
        """Initialize the Azure OpenAI client."""
        self.endpoint = "https://smarttsg-gpt.openai.azure.com/"
        self.api_version = "2024-08-01-preview"
        token_provider = get_bearer_token_provider(
            DefaultAzureCredential(),
            "https://cognitiveservices.azure.com/.default",
        )
        self.model = "gpt-4o"
        self.client = AzureOpenAI(
            azure_deployment=self.model,
            azure_endpoint=self.endpoint,
            api_version=self.api_version,
            azure_ad_token_provider=token_provider,
        )
        self.kwargs = kwargs or {}

    def response(
        self,
        messages: list,
        output_format: type,
    ) -> list[dict]:
        """Get a response from the Azure OpenAI service."""
        r = self.client.beta.chat.completions.parse(
            model=self.model,
            messages=messages,
            response_format=output_format,
            **self.kwargs,
        )
        content_str = r.choices[0].message.content
        try:
            return json.loads(content_str)
        except json.JSONDecodeError as e:
            msg = f"Failed to parse JSON response: {e}"
            raise ValueError(msg) from e
        except Exception as e:
            msg = f"Unexpected error: {e}"
            raise ValueError(msg) from e
