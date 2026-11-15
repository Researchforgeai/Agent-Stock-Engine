import unittest
from types import SimpleNamespace

from stock_analysis.adapters.outbound.mcp import (
    NseMcpServer,
    NseMcpSettings,
    NseMcpToolError,
    NseMcpToolNotFound,
    NseMcpClient,
)


class FakeClient:
    def __init__(self, url):
        self.url = url
        self.closed = False
        self.calls = []
        self.fail_tool = False

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, traceback):
        self.closed = True

    async def list_tools(self):
        return SimpleNamespace(
            tools=[
                SimpleNamespace(
                    name="get_quote",
                    description="Return a quote",
                    input_schema={"type": "object", "properties": {}},
                )
            ]
        )

    async def call_tool(self, name, arguments):
        self.calls.append((name, arguments))
        return SimpleNamespace(
            is_error=self.fail_tool,
            structured_content=None if self.fail_tool else {"last": 123.45},
            content=[SimpleNamespace(text="upstream failure")] if self.fail_tool else [],
        )


class NseMcpClientTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.clients = []

        def factory(url):
            client = FakeClient(url)
            self.clients.append(client)
            return client

        settings = NseMcpSettings()
        self.client = NseMcpClient(settings, client_factory=factory)
        await self.client.__aenter__()

    async def asyncTearDown(self):
        await self.client.__aexit__(None, None, None)

    async def test_discovers_tools_for_both_endpoints(self):
        discovered = self.client.list_tools()

        self.assertEqual(len(discovered), 2)
        self.assertEqual(
            {tool.server for tool in discovered},
            {NseMcpServer.BHAVCOPY, NseMcpServer.CM_MARKET},
        )
        self.assertEqual(len(self.client.list_tools(NseMcpServer.BHAVCOPY)), 1)

    async def test_calls_only_advertised_tools_and_preserves_structured_result(self):
        result = await self.client.call_tool(
            NseMcpServer.BHAVCOPY,
            "get_quote",
            {"symbol": "NIFTY"},
        )

        self.assertEqual(result.structured_content, {"last": 123.45})
        self.assertEqual(self.clients[0].calls, [("get_quote", {"symbol": "NIFTY"})])

    async def test_rejects_unknown_tool(self):
        with self.assertRaises(NseMcpToolNotFound):
            await self.client.call_tool(NseMcpServer.BHAVCOPY, "unknown", {})

    async def test_surfaces_upstream_tool_errors(self):
        self.clients[0].fail_tool = True

        with self.assertRaisesRegex(NseMcpToolError, "upstream failure"):
            await self.client.call_tool(NseMcpServer.BHAVCOPY, "get_quote", {})

    async def test_requires_connection_context(self):
        disconnected = NseMcpClient(client_factory=lambda _: FakeClient("unused"))

        with self.assertRaisesRegex(RuntimeError, "async with"):
            disconnected.list_tools()


class NseMcpSettingsTests(unittest.TestCase):
    def test_rejects_non_nse_or_non_https_endpoint(self):
        with self.assertRaises(ValueError):
            NseMcpSettings(bhavcopy_url="http://example.com/mcp")


if __name__ == "__main__":
    unittest.main()
