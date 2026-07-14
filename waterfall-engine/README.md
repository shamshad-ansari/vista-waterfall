# Waterfall Engine

Pure calculation library for PE fund waterfall distributions: return of capital, preferred return, GP catch-up, and residual split.

## Run locally

```bash
cd waterfall-engine
pip install -e ".[dev]"
pytest tests/ -v
```

## Package

| Module | Description |
|---|---|
| `models` | `FundTerms`, `InvestmentTranche`, `WaterfallState`, `WaterfallInput` |
| `rules` | The four pooled/deal-level tier functions, each taking and returning a `WaterfallState` |
| `engine.waterfall_engine` | `run_waterfall(input) -> WaterfallState` — fixed tier orchestration |
| `validators.validator` | `validate_input(input)` happy-path checks, raises `WaterfallValidationError` |

Scope: pooled, deal-level tier math only (no per-LP allocation). Not yet wired into `waterfall-scenario-mcp`.
