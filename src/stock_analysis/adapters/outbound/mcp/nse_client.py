"""Client-side tool access to NSE's hosted MCP servers."""

from __future__ import annotations

from contextlib import AsyncExitStack
from dataclasses import dataclass
from enum import Enum
from typing import Any, Mapping, Protocol

from mcp import Client

from stock_analysis.adapters.outbound.mcp.nse_settings import NseMcpSettings


class NseMcpServer(str, Enum):
    BHAVCOPY = "nse-bhavcopy"
    CM_MARKET = "cm-market"


@dataclass(frozen=True)
class NseMcpTool:
    server: NseMcpServer
    name: str
    description: str | None
    input_schema: Mapping[str, Any]


@dataclass(frozen=True)
class NseMcpResult:
    structured_content: Any
    content: tuple[Mapping[str, Any], ...]


class NseMcpToolError(RuntimeError):
    """Raised when an NSE MCP tool returns an MCP-level error."""


class NseMcpToolNotFound(LookupError):
    """Raised when a requested tool is not advertised by its NSE server."""


class _Client(Protocol):
    async def list_tools(self) -> Any: ...

    async def call_tool(self, name: str, arguments: dict[str, Any]) -> Any: ...


class NseMcpClient:
    """Discover and call tools from the two official NSE MCP endpoints.

    Use as an async context manager so each remote MCP session is opened once
    and closed reliably by the application composition root.
    """

    def __init__(
        self,
        settings: NseMcpSettings | None = None,
        *,
        client_factory: Any = Client,
    ) -> None:
        self._settings = settings or NseMcpSettings.from_env()
        self._client_factory = client_factory
        self._stack: AsyncExitStack | None = None
        self._clients: dict[NseMcpServer, _Client] = {}
        self._tools: dict[NseMcpServer, tuple[NseMcpTool, ...]] = {}

    async def __aenter__(self) -> NseMcpClient:
        if self._stack is not None:
            raise RuntimeError("NSE MCP client is already connected")

        stack = AsyncExitStack()
        endpoints = {
            NseMcpServer.BHAVCOPY: self._settings.bhavcopy_url,
            NseMcpServer.CM_MARKET: self._settings.cm_market_url,
        }
        try:
            for server, url in endpoints.items():
                client = await stack.enter_async_context(self._client_factory(url))
                self._clients[server] = client
                response = await client.list_tools()
                self._tools[server] = tuple(
                    NseMcpTool(
                        server=server,
                        name=tool.name,
                        description=getattr(tool, "description", None),
                        input_schema=getattr(tool, "input_schema", {}),
                    )
                    for tool in response.tools
                )
        except BaseException:
            await stack.aclose()
            self._clients.clear()
            self._tools.clear()
            raise

        self._stack = stack
        return self

    async def __aexit__(self, exc_type: Any, exc: Any, traceback: Any) -> None:
        stack, self._stack = self._stack, None
        self._clients.clear()
        self._tools.clear()
        if stack is not None:
            await stack.__aexit__(exc_type, exc, traceback)

    def list_tools(self, server: NseMcpServer | None = None) -> tuple[NseMcpTool, ...]:
        self._require_connected()
        if server is not None:
            return self._tools[self._coerce_server(server)]
        return tuple(tool for tools in self._tools.values() for tool in tools)

    async def call_tool(
        self,
        server: NseMcpServer,
        name: str,
        arguments: Mapping[str, Any],
    ) -> NseMcpResult:
        self._require_connected()
        selected_server = self._coerce_server(server)
        if not any(tool.name == name for tool in self._tools[selected_server]):
            raise NseMcpToolNotFound(
                f"{name!r} is not advertised by {selected_server.value}"
            )

        response = await self._clients[selected_server].call_tool(name, dict(arguments))
        if response.is_error:
            detail = "; ".join(
                str(getattr(block, "text", ""))
                for block in response.content
                if getattr(block, "text", None)
            )
            raise NseMcpToolError(
                f"NSE MCP tool {selected_server.value}/{name} failed"
                + (f": {detail}" if detail else "")
            )

        return NseMcpResult(
            structured_content=response.structured_content,
            content=tuple(_serialize_content(block) for block in response.content),
        )

    def _require_connected(self) -> None:
        if self._stack is None:
            raise RuntimeError("Use NseMcpClient inside 'async with'")

    @staticmethod
    def _coerce_server(server: NseMcpServer | str) -> NseMcpServer:
        try:
            return NseMcpServer(server)
        except ValueError as exc:
            raise ValueError(f"Unsupported NSE MCP server: {server!r}") from exc


def _serialize_content(block: Any) -> Mapping[str, Any]:
    model_dump = getattr(block, "model_dump", None)
    if callable(model_dump):
        return model_dump(mode="json")
    if isinstance(block, Mapping):
        return block
    text = getattr(block, "text", None)
    if text is not None:
        return {"type": "text", "text": text}
    return {"type": type(block).__name__}
