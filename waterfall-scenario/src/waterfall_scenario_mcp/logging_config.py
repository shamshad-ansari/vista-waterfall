"""Logging configuration for waterfall scenario MCP (stderr for stdio transport)."""

import logging
import sys

LOGGER_NAME = "waterfall_scenario_mcp"


def configure_logging(level: int = logging.INFO) -> logging.Logger:
    """Configure structured logging to stderr."""
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        stream=sys.stderr,
        force=True,
    )
    return logging.getLogger(LOGGER_NAME)
