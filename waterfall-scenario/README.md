# Waterfall Scenario MCP

FastMCP server that computes a draft LP waterfall distribution scenario from
a confirmed exit valuation.

## Run locally

```bash
cd waterfall-scenario
pip install -e ./../mock-data
pip install -e ./../waterfall-engine
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
| `waterfall_scenario_compute_lp_distributions` | Loads fund rules and the LP roster via `mock_data.get_fund_rules` / `mock_data.get_lp_roster` (Tool A — Fund & Investor Static Tool stand-in) and the investment's cashflow tranches via `mock_data.get_cashflows` (Tool B — Accounting Cashflows Tool stand-in), runs the pooled American/deal-by-deal tier sequence via `waterfall_engine.run_waterfall`, then splits the LP-tier-total across the roster via `waterfall_engine.allocate_lp_distributions` |

## Reasoning

Implements `mock_datasets_Final_12pm.md` §0.2/§2 end-to-end:

1. Take the confirmed exit valuation (the Valuation Agent's `confirmed_total_valuation`) as `distributable_cash`.
2. Load fund terms (`mock_data.get_fund_rules`) and the investment's dated tranches (`mock_data.get_cashflows`).
3. Run the pooled tier sequence: return of capital, preferred return, GP catch-up, residual split (`waterfall_engine.run_waterfall`).
4. Load the 10-LP roster (`mock_data.get_lp_roster`) and split the resulting LP-tier-total pro-rata by fund commitment % (`waterfall_engine.allocate_lp_distributions`).
5. Return the draft distribution scenario, `status: "PENDING_HITL_APPROVAL"` — a human GP still has to verify it.

On the Meridian golden path (confirmed valuation $340,000,000, fund `AGF3-2018`, investment `MSC-2019-047`), this reconciles to the mock dataset's own figures within a small tolerance (see `waterfall-engine`'s rounding note): return of capital $208,000,000, LP total ≈$313,600,000, GP total ≈$26,400,000, LP-003 ≈$69,688,889.

## Depends on

- [`mock-data`](../mock-data) — stand-in for the missing Fund & Investor Static / Accounting Cashflows tools, installed as a path dependency.
- [`waterfall-engine`](../waterfall-engine) — the pure tier + allocation calculation engine, installed as a path dependency.

## Tests

```bash
pip install -e ".[dev]"
pytest tests/ -v
```
