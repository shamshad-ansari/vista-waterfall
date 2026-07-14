# Valuation MCP — Agent Guide

> Generic MCP construction standards: [`../AGENTS.md`](../AGENTS.md)

## Architectural decision

The valuation capability is exposed as a **standalone MCP server** under `src/mcps/valuation/`, built with **FastMCP (Python)** and **stdio transport**.

| Choice | Rationale |
|---|---|
| FastMCP | Matches project MCP stack; minimal boilerplate for tool registration |
| Python | Aligns with backend/data workflows; Pydantic for typed schemas |
| stdio | Local agent use; simple Cursor/CLI wiring; no HTTP auth yet |
| Separate package | Isolates valuation from agents/backend; one MCP per domain |

## Purpose

Computes **asset valuation** from a **position closing price**. Agents call this MCP instead of embedding valuation logic in prompts.

**Current state (scaffold):** inputs and outputs are **hardcoded**. The tool ignores caller parameters and returns demo values until real pricing/valuation services are connected.

## Server identity

- **Package:** `valuation-mcp` (`src/mcps/valuation/`)
- **MCP name:** `valuation_mcp`
- **Entry point:** `valuation-mcp` or `python -m valuation_mcp.server`

## Tools

### `valuation_get_asset_valuation`

| | |
|---|---|
| **Input** | None (scaffold) — future: `closing_price`, `position_id` |
| **Output** | JSON `ValuationOutput`: `position_id`, `closing_price`, `asset_valuation`, `currency`, `valuation_method` |
| **Hardcoded demo** | `POS-001`, closing price `125.50`, asset valuation `1_250_000.00` USD |
| **Hints** | read-only, idempotent, not open-world |

## Schemas

Defined in `src/valuation_mcp/schemas/valuation.py`:

- `ValuationInput` — future tool parameters (`closing_price`, `position_id`)
- `ValuationOutput` — structured response agents should parse

## Agent usage

1. Prefer **`valuation_get_asset_valuation`** over guessing valuations in text.
2. Parse the JSON response; use `asset_valuation` as the canonical number.
3. Treat `valuation_method: "hardcoded_scaffold"` as a signal that values are placeholders.
4. Do not assume live market data until `valuation_method` changes and inputs are accepted.

## Wiring in Cursor

Add to MCP config (example):

```json
{
  "mcpServers": {
    "valuation": {
      "command": "valuation-mcp",
      "cwd": "src/mcps/valuation"
    }
  }
}
```

Install first: `pip install -e .` from `src/mcps/valuation/`.

## Extension path

1. Accept `ValuationInput` on the tool handler.
2. Call backend valuation API or pricing service from `tools/get_valuation.py`.
3. Remove hardcoded constants; keep `ValuationOutput` as the stable contract.
4. Add tests under `tests/` before production use.

## Related paths

- MCP root overview: `src/mcps/README.md`
- Valuation package readme: `src/mcps/valuation/README.md`
