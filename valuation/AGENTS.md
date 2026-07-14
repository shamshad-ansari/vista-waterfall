# Valuation MCP — Agent Guide

> Generic MCP construction standards: [`../AGENTS.md`](../AGENTS.md)

## Architectural decision

The valuation capability is exposed as a **standalone MCP server** under `valuation/`, built with **FastMCP (Python)** and **stdio transport**.

| Choice | Rationale |
|---|---|
| FastMCP | Matches project MCP stack; minimal boilerplate for tool registration |
| Python | Aligns with backend/data workflows; Pydantic for typed schemas |
| stdio | Local agent use; simple Cursor/CLI wiring; no HTTP auth yet |
| Separate package | Isolates valuation from agents/backend; one MCP per domain |

## Purpose

Runs the Valuation Agent's reasoning from `mock_datasets_Final_12pm.md` §1.4: reasons across **Tool A** (native Ledger Data Tool — asset + tranche record) and **Tool B** (customer-registered Price Feed Tool — the new tranche's closing price) to derive an implied enterprise value, restate all tranches against it, run validation checks, and return a confirmed valuation.

**Current state:** real reasoning, backed by the [`mock-data`](../mock-data) package as the stand-in for Tool A (always) and, when the caller doesn't supply price-feed fields directly, also for Tool B (`mock_data.get_price_feed_response`). This package has no dependency on `peak_contracts` and shouldn't gain one.

## Server identity

- **Package:** `valuation-mcp` (`valuation/`)
- **MCP name:** `valuation_mcp`
- **Entry point:** `valuation-mcp` or `python -m valuation_mcp.server`

## Tools

### `valuation_get_asset_valuation`

| | |
|---|---|
| **Input** | `ValuationInput`: `asset_id` (required), plus the Tool B price-feed fields — `closing_price_per_unit`, `methodology`, `ic_approved_by`, `effective_date`, `arm_length_confirmation` (all optional; omit all to use the demo price feed stand-in) |
| **Output** | JSON `ValuationOutput`: `asset_id`, `confirmed_total_valuation`, `valuation_per_unit`, `methodology`, `effective_date`, `tranche_values`, `prior_total_carrying_value`, `valuation_uplift`, `validation_status`, `validation_checks`, `source_tool` |
| **Reasoning** | `valuation_mcp.reasoning.value_asset` — see below |
| **Hints** | read-only, idempotent, not open-world |

## Reasoning (`valuation_mcp/reasoning.py`)

1. `mock_data.get_asset_record(asset_id)` — asset + all tranches.
2. Identify the one tranche with no `prior_mark_per_unit` (the unpriced tranche).
3. Get its closing price — from the input if supplied, else `mock_data.get_price_feed_response(asset_id, tranche_id)`.
4. `confirmed_total_valuation = closing_price_per_unit × total_units_across_all_tranches`.
5. Restate every tranche's value at the new per-unit price → `tranche_values`.
6. Run 5 validation checks (price present/positive, arm's-length confirmed, IC approval present, uplift vs. weighted prior mark within ±50%, units reconcile to ledger) → `validation_status`.

## Schemas

Defined in `src/valuation_mcp/schemas/valuation.py`:

- `ValuationInput` — `asset_id` + optional Tool B price-feed fields
- `ValuationOutput` — confirmed valuation result agents should parse
- `ValidationCheck` — one entry per validation check, in `ValuationOutput.validation_checks`

## Agent usage

1. Prefer **`valuation_get_asset_valuation`** over guessing valuations in text.
2. Parse the JSON response; use `confirmed_total_valuation` and `tranche_values` as the canonical numbers.
3. Check `validation_status` — if it starts with `FAILED`, inspect `validation_checks` for which check(s) failed before treating the valuation as confirmed.

## Wiring in Cursor

Add to MCP config (example):

```json
{
  "mcpServers": {
    "valuation": {
      "command": "valuation-mcp",
      "cwd": "valuation"
    }
  }
}
```

Install first (from repo root): `pip install -e ./mock-data && pip install -e ./valuation`.

## Related paths

- MCP root overview: `../AGENTS.md`
- Mock data package: `../mock-data`
