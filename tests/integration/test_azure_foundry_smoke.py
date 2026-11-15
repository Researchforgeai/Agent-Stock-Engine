import os
import unittest

from stock_analysis.adapters.outbound.llm.azure_foundry import create_chat_model


@unittest.skipUnless(
    os.getenv("RUN_AZURE_FOUNDRY_SMOKE_TEST") == "1",
    "Set RUN_AZURE_FOUNDRY_SMOKE_TEST=1 to call Azure AI Foundry",
)
class AzureFoundrySmokeTests(unittest.IsolatedAsyncioTestCase):
    async def test_chat_model_returns_a_response(self):
        model = create_chat_model()

        response = await model.ainvoke("Reply with the single word OK.")

        self.assertTrue(response.content.strip())


if __name__ == "__main__":
    unittest.main()
