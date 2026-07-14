# Mock Data

Demo dataset stand-in for the missing database. There is no real backend behind the Ledger Data Tool, Fund & Investor Static Tool, or Accounting Cashflows Tool for this hackathon — this package *is* that backend, hardcoding the single Meridian Software Group / Acme Growth Fund III (AGF3-2018) scenario from `mock_datasets_Final_12pm.md`.

## Run locally

```bash
cd mock-data
pip install -e ".[dev]"
pytest tests/ -v
```

## Package

| Function | Returns | Source section |
|---|---|---|
| `get_asset_record(asset_id)` | `AssetRecord` (asset header + 3 tranches) | §1.1–1.2 |
| `get_price_feed_response(asset_id, tranche_id)` | `PriceFeedResponse` | §1.3 |
| `get_fund_rules(fund_id)` | `FundRules` | §2.1 |
| `get_lp_roster(fund_id)` | `list[LPCommitment]` | §2.7 |
| `get_cashflows(investment_id)` | `CashflowRecord` | §2.2 |

Since there's only one scenario, each lookup validates the requested id and raises a clear "unknown id" error (`UnknownAssetError`, `UnknownFundError`, `UnknownInvestmentError`) for anything else — no general multi-fund lookup.

`valuation-mcp` and `waterfall-scenario-mcp` depend on this package, not the other way around. Models here are plain pydantic `BaseModel`s local to this package — no dependency on `waterfall_engine`.
