"""Azure AI Foundry chat model configuration and construction."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from urllib.parse import urlsplit

from langchain_azure_ai.chat_models import AzureAIOpenAIApiChatModel
from langchain_core.language_models import BaseChatModel


@dataclass(frozen=True)
class AzureFoundrySettings:
    endpoint: str
    api_key: str = field(repr=False)
    model: str

    def __post_init__(self) -> None:
        parsed = urlsplit(self.endpoint)
        if (
            parsed.scheme != "https"
            or not parsed.hostname
            or parsed.username is not None
            or parsed.password is not None
        ):
            raise ValueError("Azure AI Foundry endpoint must be an HTTPS URL")
        if not self.api_key.strip():
            raise ValueError("Azure AI Foundry API key must not be empty")
        if not self.model.strip():
            raise ValueError("Azure AI Foundry model must not be empty")

    @classmethod
    def from_env(cls) -> AzureFoundrySettings:
        variable_names = (
            "AZURE_AI_FOUNDRY_ENDPOINT",
            "AZURE_AI_FOUNDRY_API_KEY",
            "AZURE_AI_FOUNDRY_MODEL",
        )
        values = {name: os.getenv(name, "").strip() for name in variable_names}
        missing = [name for name, value in values.items() if not value]
        if missing:
            raise ValueError(
                "Missing required Azure AI Foundry environment variables: "
                + ", ".join(missing)
            )

        return cls(
            endpoint=values["AZURE_AI_FOUNDRY_ENDPOINT"],
            api_key=values["AZURE_AI_FOUNDRY_API_KEY"],
            model=values["AZURE_AI_FOUNDRY_MODEL"],
        )


def create_chat_model(
    settings: AzureFoundrySettings | None = None,
) -> BaseChatModel:
    """Create the LangChain-standard chat model for the configured Foundry deployment."""
    config = settings or AzureFoundrySettings.from_env()
    return AzureAIOpenAIApiChatModel(
        endpoint=config.endpoint,
        credential=config.api_key,
        model=config.model,
        max_retries=2,
    )
