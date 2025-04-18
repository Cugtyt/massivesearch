"""Model module."""

import json

from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from openai import AsyncAzureOpenAI

from massivesearch.model.base import BaseAIClient


class AzureOpenAIClient(BaseAIClient):
    """A client wrapper for interacting with the Azure OpenAI service."""

    endpoint: str = "https://smarttsg-gpt.openai.azure.com/"
    api_version: str = "2024-08-01-preview"
    model: str = "gpt-4o"
    temperature: float

    async def response(
        self,
        messages: list,
        format_model: type,
    ) -> dict:
        """Get a response from the Azure OpenAI service."""
        token_provider = get_bearer_token_provider(
            DefaultAzureCredential(),
            "https://cognitiveservices.azure.com/.default",
        )
        client = AsyncAzureOpenAI(
            azure_deployment=self.model,
            azure_endpoint=self.endpoint,
            api_version=self.api_version,
            azure_ad_token_provider=token_provider,
        )
        r = await client.beta.chat.completions.parse(
            model=self.model,
            messages=messages,
            response_format=format_model,
            temperature=self.temperature,
        )
        content_str = r.choices[0].message.content
        if not content_str or not isinstance(content_str, str):
            msg = "Empty response from Azure OpenAI."
            raise ValueError(msg)
        try:
            return json.loads(content_str)
        except json.JSONDecodeError as e:
            msg = f"Failed to parse JSON response: {e}"
            raise ValueError(msg) from e
        except Exception as e:
            msg = f"Unexpected error: {e}"
            raise ValueError(msg) from e
