# MCP Gateway

Aggregating MCP server that mounts `valuation-mcp` and
`waterfall-scenario-mcp` under a single connection, so an end user adds one
Claude connector instead of one per domain server. See
[docs/adr/008-aggregating-gateway-mcp.md](../docs/adr/008-aggregating-gateway-mcp.md)
for the design rationale.

Neither domain server is modified — each is launched as its own local stdio
subprocess (the same console script Claude Desktop launches directly per
issue 007), and this gateway forwards `list_tools`/`call_tool` through to
whichever backend owns the requested tool.

## Run locally

```bash
cd mcp-gateway
pip install -e ./../valuation
pip install -e ./../waterfall-scenario
pip install -e .
mcp-gateway
```

Or: `python -m mcp_gateway.server`

## Wiring into Claude Desktop

Replace the two separate `valuation-mcp` / `waterfall-scenario-mcp` entries
in `claude_desktop_config.json` with one:

```json
{
  "mcpServers": {
    "mcp-gateway": {
      "command": "/absolute/path/to/vista-waterfall/.venv/bin/mcp-gateway",
      "args": []
    }
  }
}
```

## Tools

Both domain servers' tools are exposed unchanged, since their names are
already domain-prefixed and don't collide:

- `valuation_get_asset_valuation`
- `waterfall_scenario_compute_lp_distributions`

If a future backend's tool name collides with an existing one, the gateway
namespaces both as `{backend_key}__{tool_name}` and fails at startup only if
that still collides.

## Depends on

- [`valuation-mcp`](../valuation) and
  [`waterfall-scenario-mcp`](../waterfall-scenario) — launched as stdio
  subprocesses, not imported directly.

## Tests

```bash
pip install -e ".[dev]"
pytest tests/ -v
```

## Remote hosting

Supports `streamable-http` the same way both backends do:

```bash
MCP_TRANSPORT=streamable_http HOST=0.0.0.0 PORT=8000 mcp-gateway
```

This is the one endpoint to host — not `valuation-mcp` and
`waterfall-scenario-mcp` separately — since it already aggregates both. See
[docs/adr/009-remote-hosting-setup.md](../docs/adr/009-remote-hosting-setup.md)
for hosting-target/auth decisions still open, and the Custom Connector setup
steps for whoever hosts this.
