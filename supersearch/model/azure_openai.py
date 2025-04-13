"""Model module."""

from typing import Self

from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from openai import AsyncAzureOpenAI
from openai.types.chat import ParsedChatCompletion


class AzureOpenAIClient:
    """A client wrapper for interacting with the Azure OpenAI service."""

    def __init__(self) -> Self:
        """Initialize the Azure OpenAI client."""
        self.endpoint = "https://smarttsg-gpt.openai.azure.com/"
        self.api_version = "2024-02-15-preview"
        token_provider = get_bearer_token_provider(
            DefaultAzureCredential(),
            "https://cognitiveservices.azure.com/.default",
        )
        self.client = AsyncAzureOpenAI(
            endpoint=self.endpoint,
            api_version=self.api_version,
            azure_ad_token_provider=token_provider,
        )
        self.model = "gpt-4o"

    async def response(
        self,
        messages: list,
        output_format: type,
    ) -> ParsedChatCompletion:
        """Get a response from the Azure OpenAI service."""
        return await self.client.beta.chat.completions.parse(
            model=self.model,
            messages=messages,
            response_format=output_format,
        )
