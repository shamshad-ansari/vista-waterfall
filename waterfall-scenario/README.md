# Waterfall Scenario MCP

FastMCP server that computes LP distribution scenarios from asset valuations.

## Run locally

```bash
cd src/mcps/waterfall-scenario
pip install -e .
waterfall-scenario-mcp
```

Or:

```bash
python -m waterfall_scenario_mcp.server
```

## Tool

| Tool | Description |
|---|---|
| `waterfall_scenario_compute_lp_distributions` | Returns LP waterfall allocations from an asset valuation |

Scaffold only: inputs and outputs are hardcoded until waterfall engine integration is wired.
