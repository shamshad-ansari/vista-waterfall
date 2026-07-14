# Waterfall Scenario MCP — Agent Guide

## Architectural decision

LP waterfall distribution logic is exposed as a **standalone MCP server** under `waterfall-scenario/`, built with **FastMCP (Python)** and **stdio transport**.

| Choice | Rationale |
|---|---|
| FastMCP | Matches project MCP stack; minimal boilerplate for tool registration |
| Python | Aligns with backend/data workflows; Pydantic for typed schemas |
| stdio | Local agent use; simple Cursor/CLI wiring; no HTTP auth yet |
| Separate package | Isolates waterfall logic from valuation and agents; one MCP per domain |

## Purpose

Runs the Waterfall Agent's reasoning from `mock_datasets_Final_12pm.md` §0.2/§2: reasons across **Tool A** (native Fund & Investor Static Tool — fund rules + LP roster) and **Tool B** (native Accounting Cashflows Tool — the investment's dated tranches and realization date), runs the pooled American/deal-by-deal tier sequence, then splits the resulting LP-tier-total across the LP roster pro-rata by fund commitment %.

**Current state:** real reasoning, backed by the [`waterfall-engine`](../waterfall-engine) package (pure tier + allocation calculation, no MCP dependency) and the [`mock-data`](../mock-data) package as the stand-in for Tool A and Tool B. This package has no dependency on `peak_contracts` — that package never existed anywhere in this repo or its dependency closure and has been dropped entirely; its old placeholder contract (`WaterfallModelInput`, `WaterfallModelOutput`, `WaterfallLpDistribution`, which mixed GP carry into the LP distribution list as a fake `GP-001` row) is gone.

**HITL context:** The GP using the software will later **verify** the scenario in the human-in-the-loop (HITL) mechanism. Agents should treat MCP output as a **proposed** distribution, not an approved one — the output's `status` field is always `"PENDING_HITL_APPROVAL"`.

## Pipeline position

```
valuation_mcp  →  waterfall_scenario_mcp  →  HITL (GP verification)
(confirmed valuation)  (draft LP distribution scenario)  (human approval)
```

1. Call `valuation_get_asset_valuation` to obtain `confirmed_total_valuation`.
2. Call `waterfall_scenario_compute_lp_distributions` with that valuation as `distributable_cash`, plus `investment_id` and `fund_id`.
3. Present the returned `lp_allocations` / `tier_results` to the GP for HITL review.

## Server identity

- **Package:** `waterfall-scenario-mcp` (`waterfall-scenario/`)
- **MCP name:** `waterfall_scenario_mcp`
- **Entry point:** `waterfall-scenario-mcp` or `python -m waterfall_scenario_mcp.server`

## Tools

### `waterfall_scenario_compute_lp_distributions`

| | |
|---|---|
| **Input** | `WaterfallInput`: `distributable_cash` (required, > 0 — the confirmed exit valuation), `investment_id` (default `MSC-2019-047`), `fund_id` (default `AGF3-2018`) |
| **Output** | JSON `WaterfallOutput`: `investment_id`, `distributable_cash`, `tier_results` (`return_of_capital`, `preferred_return`, `gp_catchup`, `lp_residual`, `gp_residual`), `lp_total`, `gp_total`, `lp_allocations` (list of `{lp_id, amount}`, LPs only — GP amounts stay in `gp_total`/`tier_results`), `status` |
| **Reasoning** | `waterfall_scenario_mcp.reasoning.compute_waterfall_scenario` — see below |
| **Hints** | read-only, idempotent, not open-world |

## Reasoning (`waterfall_scenario_mcp/reasoning.py`)

1. `mock_data.get_fund_rules(fund_id)` — hurdle rate, carry split, catch-up structure → `waterfall_engine.FundTerms`.
2. `mock_data.get_cashflows(investment_id)` — investment tranches with dates/amounts and the realization date → `waterfall_engine.InvestmentTranche` list.
3. `mock_data.get_lp_roster(fund_id)` — LP commitments → `waterfall_engine.LPCommitment` list.
4. Build `waterfall_engine.WaterfallInput` (`distributable_cash` = the tool's confirmed valuation input) and call `waterfall_engine.run_waterfall(...)` — the pooled tier sequence (return of capital, preferred return, GP catch-up, residual split).
5. Call `waterfall_engine.allocate_lp_distributions(state.lp_total, roster)` for the per-LP pro-rata split.

## Schemas

Defined locally in `src/waterfall_scenario_mcp/schemas/waterfall.py` (no external contract package):

- `WaterfallInput` — `investment_id`, `fund_id`, `distributable_cash`
- `WaterfallOutput` — draft distribution scenario agents should parse
- `TierResults` — the 5 pooled tier amounts, one entry in `WaterfallOutput.tier_results`
- `LPAllocation` — one LP's `{lp_id, amount}` row, in `WaterfallOutput.lp_allocations`

## Agent usage

1. Prefer **`waterfall_scenario_compute_lp_distributions`** over computing LP splits in free text.
2. Parse the JSON response; use `lp_allocations` as the canonical per-LP allocation table, `tier_results`/`lp_total`/`gp_total` for the deal-level breakdown.
3. Treat `status: "PENDING_HITL_APPROVAL"` as a hard signal — do not present as a final/approved distribution until HITL confirms.
4. **Do not surface tier-by-tier calculation logic to external parties** — the product's explainability constraint permits only a single summary line externally (e.g. "Calculated against LPA terms: 8% hurdle, 20% carry, 1x preferred return. All LP capital accounts current."). `tier_results` is for the orchestrator-to-orchestrator handoff, not direct UI display.

## Wiring in Cursor

Add to MCP config (example):

```json
{
  "mcpServers": {
    "waterfall-scenario": {
      "command": "waterfall-scenario-mcp",
      "cwd": "waterfall-scenario"
    }
  }
}
```

Install first (from repo root): `pip install -e ./mock-data && pip install -e ./waterfall-engine && pip install -e ./waterfall-scenario`.

## Related paths

- Upstream valuation MCP: `../valuation/AGENTS.md`
- Calculation engine: `../waterfall-engine`
- Mock data package: `../mock-data`
