"""Aggregating gateway MCP server.

Mounts valuation-mcp and waterfall-scenario-mcp under a single MCP
connection, per docs/adr/008-aggregating-gateway-mcp.md. Neither domain
server is modified: each is launched as its own local stdio subprocess
(same console script Claude Desktop launches directly per issue 007) and
this gateway forwards list_tools/call_tool through to whichever backend
owns the requested tool.

The installed `mcp` SDK's FastMCP has no built-in mount()/proxy support
(checked: 1.28.1's FastMCP exposes no such method), so this overrides
FastMCP.list_tools / FastMCP.call_tool directly rather than fighting the
tool-decorator machinery, which is designed around introspecting typed
Python functions, not forwarding an already-defined remote tool schema.
"""

import os
from contextlib import AsyncExitStack, asynccontextmanager
from typing import Any

from mcp import ClientSession, types
from mcp.client.stdio import StdioServerParameters, stdio_client
from mcp.server.fastmcp import FastMCP

from mcp_gateway.config import BACKENDS
from mcp_gateway.logging_config import LOGGER_NAME, configure_logging

logger = configure_logging()


class GatewayMCP(FastMCP):
    """FastMCP server whose tool list/dispatch is forwarded to backend servers."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._backend_sessions: dict[str, ClientSession] = {}
        self._tool_owner: dict[str, str] = {}  # exposed tool name -> backend key

    def register_backend(self, backend_key: str, session: ClientSession) -> None:
        self._backend_sessions[backend_key] = session

    async def list_tools(self) -> list[types.Tool]:
        aggregated: list[types.Tool] = []
        seen_names: dict[str, str] = {}  # tool name -> backend key that claimed it

        for backend_key, session in self._backend_sessions.items():
            result = await session.list_tools()
            for tool in result.tools:
                exposed_name = tool.name
                if exposed_name in seen_names:
                    # Collision: two backends produced the same tool name.
                    # Namespace both instead of silently letting one shadow
                    # the other. If that *still* collides, fail loud rather
                    # than serve an ambiguous tool list.
                    other_key = seen_names[exposed_name]
                    logger.warning(
                        "Tool name collision on %r between backends %r and %r; namespacing both",
                        exposed_name,
                        other_key,
                        backend_key,
                    )
                    renamed = f"{backend_key}__{tool.name}"
                    if renamed in seen_names or renamed in self._tool_owner:
                        raise RuntimeError(
                            f"Unresolvable tool name collision on {tool.name!r} "
                            f"between backends {other_key!r} and {backend_key!r}"
                        )
                    exposed_name = renamed

                seen_names[exposed_name] = backend_key
                self._tool_owner[exposed_name] = backend_key
                aggregated.append(
                    tool if exposed_name == tool.name else tool.model_copy(update={"name": exposed_name})
                )

        return aggregated

    async def call_tool(self, name: str, arguments: dict[str, Any]) -> types.CallToolResult:
        backend_key = self._tool_owner.get(name)
        if backend_key is None:
            # Tool list may not have been fetched yet on this connection path.
            await self.list_tools()
            backend_key = self._tool_owner.get(name)
        if backend_key is None:
            raise ValueError(f"Unknown tool: {name!r}")

        session = self._backend_sessions[backend_key]
        # Namespaced names (backend_key__original_name) need the original
        # name when forwarded to the backend that owns them.
        backend_tool_name = name.removeprefix(f"{backend_key}__")
        return await session.call_tool(backend_tool_name, arguments)


@asynccontextmanager
async def lifespan(app: GatewayMCP):
    async with AsyncExitStack() as stack:
        for backend_key, backend_cfg in BACKENDS.items():
            params = StdioServerParameters(
                command=backend_cfg["command"],
                args=backend_cfg.get("args", []),
            )
            read, write = await stack.enter_async_context(stdio_client(params))
            session = await stack.enter_async_context(ClientSession(read, write))
            await session.initialize()
            app.register_backend(backend_key, session)
            logger.info("Connected backend %r (%s)", backend_key, backend_cfg["command"])

        logger.info("%s gateway started and ready (%d backends)", LOGGER_NAME, len(BACKENDS))
        yield
        logger.info("%s gateway shutting down", LOGGER_NAME)


_default_host = "0.0.0.0" if os.getenv("MCP_TRANSPORT") == "streamable_http" else "127.0.0.1"

mcp = GatewayMCP(
    "mcp_gateway",
    lifespan=lifespan,
    host=os.getenv("HOST", _default_host),
    port=int(os.getenv("PORT", "8000")),
)


def main() -> None:
    """Entry point for stdio (local) or streamable_http transport."""
    transport = os.getenv("MCP_TRANSPORT", "stdio")
    if transport == "streamable_http":
        host = os.getenv("HOST", "0.0.0.0")
        port = int(os.getenv("PORT", "8000"))
        logger.info("Starting %s gateway (streamable-http) on %s:%s...", LOGGER_NAME, host, port)
        mcp.run(transport="streamable-http")
        return

    logger.info("Starting %s gateway (stdio)...", LOGGER_NAME)
    mcp.run()


if __name__ == "__main__":
    main()
