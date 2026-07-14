# Waterfall Scenario MCP — Agent Guide

## Architectural decision

LP waterfall distribution logic is exposed as a **standalone MCP server** under `src/mcps/waterfall-scenario/`, built with **FastMCP (Python)** and **stdio transport**.

| Choice | Rationale |
|---|---|
| FastMCP | Matches project MCP stack; minimal boilerplate for tool registration |
| Python | Aligns with backend/data workflows; Pydantic for typed schemas |
| stdio | Local agent use; simple Cursor/CLI wiring; no HTTP auth yet |
| Separate package | Isolates waterfall logic from valuation and agents; one MCP per domain |

## Purpose

Computes a **waterfall scenario** — how an asset valuation is distributed across LPs (and GP carry) — from an **asset valuation** input. Agents call this MCP instead of embedding waterfall logic in prompts.

**Override role:** This MCP is the **reference override** for the `waterfall-model` node's `waterfall-model` contract (mode `replace`). Its schemas are the frozen contract models in `peak_contracts`; the tool satisfies `contracts/waterfall-model.json`.

**HITL context:** The GP using the software will later **verify** the scenario in the human-in-the-loop (HITL) mechanism. Agents should treat MCP output as a **proposed** distribution, not an approved one.

**Current state (scaffold):** the tool accepts contract inputs but returns **hardcoded** demo distributions until the real waterfall engine is connected.

## Pipeline position

```
valuation_mcp  →  waterfall_scenario_mcp  →  HITL (GP verification)
(asset value)     (LP distribution split)     (human approval)
```

1. Call `valuation_get_asset_valuation` to obtain `asset_valuation`.
2. Call `waterfall_scenario_compute_lp_distributions` with that valuation (future; scaffold ignores input).
3. Present `lp_distributions` to the GP for HITL review.

## Server identity

- **Package:** `waterfall-scenario-mcp` (`src/mcps/waterfall-scenario/`)
- **MCP name:** `waterfall_scenario_mcp`
- **Entry point:** `waterfall-scenario-mcp` or `python -m waterfall_scenario_mcp.server`

## Tools

### `waterfall_scenario_compute_lp_distributions`

| | |
|---|---|
| **Input** | `asset_valuation` (required, > 0), `fund_id` (default `FUND-001`) — scaffold ignores values for computation |
| **Output** | JSON `WaterfallOutput`: `fund_id`, `asset_valuation`, `currency`, `waterfall_method`, `lp_distributions`, `total_distributed` |
| **Hardcoded demo** | Fund `FUND-001`, valuation `1_250_000.00` USD split across 3 LPs + GP carry |
| **Hints** | read-only, idempotent, not open-world |

## Schemas

Source of truth is `peak_contracts.models.waterfall_model`; `src/waterfall_scenario_mcp/schemas/waterfall.py` re-exports them:

- `WaterfallInput` (`WaterfallModelInput`) — tool parameters (`asset_valuation`, `fund_id`)
- `LPDistribution` (`WaterfallLpDistribution`) — per-LP allocation row (`lp_id`, `lp_name`, `class`, `distribution_amount`)
- `WaterfallOutput` (`WaterfallModelOutput`) — structured response agents should parse

## Agent usage

1. Prefer **`waterfall_scenario_compute_lp_distributions`** over computing LP splits in free text.
2. Parse the JSON response; use `lp_distributions` as the canonical allocation table.
3. Treat `waterfall_method: "hardcoded_scaffold"` as a signal that values are placeholders.
4. Label results as **pending GP verification** — do not present as final until HITL confirms.
5. Ensure `total_distributed` equals `asset_valuation` before surfacing to users (scaffold guarantees this).

## Wiring in Cursor

Add to MCP config (example):

```json
{
  "mcpServers": {
    "waterfall-scenario": {
      "command": "waterfall-scenario-mcp",
      "cwd": "src/mcps/waterfall-scenario"
    }
  }
}
```

Install first: `pip install -e .` from `src/mcps/waterfall-scenario/`.

## Extension path

1. Wire the accepted `WaterfallInput` (`asset_valuation`) to real computation instead of ignoring it.
2. Call backend waterfall engine from `tools/get_waterfall_scenario.py`.
3. Remove hardcoded constants; keep the `peak_contracts` `WaterfallModelOutput` as the stable contract.
4. Add HITL status fields (`status`, `verified_by`, `verified_at`) when the review API exists.
5. Add tests under `tests/` before production use.

## Related paths

- MCP root overview: `src/mcps/README.md`
- Upstream valuation MCP: `src/mcps/valuation/AGENTS.md`
- Package readme: `src/mcps/waterfall-scenario/README.md`
