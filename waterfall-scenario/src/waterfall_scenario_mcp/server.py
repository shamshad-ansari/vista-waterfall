import os
from contextlib import asynccontextmanager

from mcp.server.fastmcp import FastMCP

from waterfall_scenario_mcp.logging_config import LOGGER_NAME, configure_logging
from waterfall_scenario_mcp.tools import register_waterfall_scenario_tools

logger = configure_logging()

_default_host = (
    "0.0.0.0" if os.getenv("MCP_TRANSPORT") == "streamable_http" else "127.0.0.1"
)


@asynccontextmanager
async def lifespan(_app: FastMCP):
    logger.info("%s server started and ready", LOGGER_NAME)
    yield
    logger.info("%s server shutting down", LOGGER_NAME)


mcp = FastMCP(
    "waterfall_scenario_mcp",
    lifespan=lifespan,
    host=os.getenv("HOST", _default_host),
    port=int(os.getenv("PORT", "8000")),
)

register_waterfall_scenario_tools(mcp)


def main() -> None:
    """Entry point for stdio (local) or streamable_http (AWS) transport."""
    transport = os.getenv("MCP_TRANSPORT", "stdio")
    if transport == "streamable_http":
        host = os.getenv("HOST", "0.0.0.0")
        port = int(os.getenv("PORT", "8000"))
        logger.info(
            "Starting %s server (streamable-http) on %s:%s...",
            LOGGER_NAME,
            host,
            port,
        )
        mcp.run(transport="streamable-http")
        return

    logger.info("Starting %s server (stdio)...", LOGGER_NAME)
    mcp.run()


if __name__ == "__main__":
    main()
