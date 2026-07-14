# Valuation MCP

FastMCP server that computes asset valuations from position closing prices.

## Run locally

```bash
cd src/mcps/valuation
pip install -e .
valuation-mcp
```

Or:

```bash
python -m valuation_mcp.server
```

## Tool

| Tool | Description |
|---|---|
| `valuation_get_asset_valuation` | Returns asset valuation from a position closing price |

Scaffold only: inputs and outputs are hardcoded until backend integration is wired.
