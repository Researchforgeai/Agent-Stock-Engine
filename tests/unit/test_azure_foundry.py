import os
import unittest
from unittest.mock import patch

from stock_analysis.adapters.outbound.llm.azure_foundry import (
    AzureFoundrySettings,
    create_chat_model,
)


class AzureFoundrySettingsTests(unittest.TestCase):
    def test_from_env_requires_endpoint_key_and_model(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaisesRegex(
                ValueError,
                "AZURE_AI_FOUNDRY_ENDPOINT.*AZURE_AI_FOUNDRY_API_KEY.*AZURE_AI_FOUNDRY_MODEL",
            ):
                AzureFoundrySettings.from_env()

    def test_requires_https_endpoint(self):
        with self.assertRaisesRegex(ValueError, "HTTPS"):
            AzureFoundrySettings(
                endpoint="http://foundry.example",
                api_key="test-key",
                model="test-model",
            )

    def test_api_key_is_not_in_settings_repr(self):
        settings = AzureFoundrySettings(
            endpoint="https://foundry.example",
            api_key="sensitive-test-key",
            model="test-model",
        )

        self.assertNotIn("sensitive-test-key", repr(settings))


class AzureFoundryModelFactoryTests(unittest.TestCase):
    @patch(
        "stock_analysis.adapters.outbound.llm.azure_foundry.AzureAIOpenAIApiChatModel"
    )
    def test_creates_provider_model_with_settings(self, model_class):
        settings = AzureFoundrySettings(
            endpoint="https://foundry.example/openai/v1/",
            api_key="test-key",
            model="test-deployment",
        )

        result = create_chat_model(settings)

        self.assertIs(result, model_class.return_value)
        model_class.assert_called_once_with(
            endpoint="https://foundry.example/openai/v1/",
            credential="test-key",
            model="test-deployment",
            max_retries=2,
        )


if __name__ == "__main__":
    unittest.main()
