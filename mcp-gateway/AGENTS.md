# MCP Gateway — Agent Guide

## Architectural decision

The gateway is a **standalone MCP server** under `mcp-gateway/`, built with
**FastMCP (Python)**, whose `list_tools`/`call_tool` are overridden to
forward to backend domain servers rather than serving tools registered on
itself. See `docs/adr/008-aggregating-gateway-mcp.md` for full rationale.

| Choice | Rationale |
|---|---|
| Subclass FastMCP, override `list_tools`/`call_tool` | Installed `mcp` SDK (1.28.1) has no `FastMCP.mount()`; this is the smallest change that reuses FastMCP's transport/run() handling |
| Backends launched as stdio subprocesses | Mirrors what Claude Desktop already does directly (issue 007); zero changes to either domain server |
| Static backend registry (`config.py`) | Two backends today; a registration protocol isn't justified until that count grows meaningfully |
| Collision handling: namespace-then-fail | No silent tool shadowing; loud at startup instead |

## Current state

Real forwarding gateway — not a design doc, not a stub. Connects to both
`valuation-mcp` and `waterfall-scenario-mcp` at startup via
`mcp.client.stdio`, discovers their tools, and forwards calls through
verbatim (`CallToolResult` passed back unmodified, including `isError` and
`structuredContent`).

## Server identity

- **Package:** `mcp-gateway` (`mcp-gateway/`)
- **MCP name:** `mcp_gateway`
- **Entry point:** `mcp-gateway` or `python -m mcp_gateway.server`

## Adding a new backend

Add an entry to `BACKENDS` in `src/mcp_gateway/config.py` with `command`
(and `args` if needed). No other code changes required — tools are
discovered at connection time, not hardcoded.

## Related paths

- Design doc: `../docs/adr/008-aggregating-gateway-mcp.md`
- Backends: `../valuation`, `../waterfall-scenario`
