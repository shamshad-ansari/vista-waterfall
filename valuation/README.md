# Valuation MCP

FastMCP server that computes a confirmed asset valuation from the ledger's
asset/tranche record and a new tranche's closing price.

## Run locally

```bash
cd valuation
pip install -e ./../mock-data
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
| `valuation_get_asset_valuation` | Loads the asset record via `mock_data.get_asset_record` (Tool A — Ledger Data Tool stand-in), derives the implied enterprise value from the newly priced tranche's closing price (from the input, or `mock_data.get_price_feed_response` as the Tool B stand-in), restates the other tranches, runs validation checks, and returns the confirmed valuation |

## Reasoning

Implements `mock_datasets_Final_12pm.md` §1.4 end-to-end:

1. Load the asset + its tranches (`mock_data.get_asset_record`) — 3 tranches, 2 priced, 1 unpriced.
2. Take the unpriced tranche's closing price (from the tool input, or the demo price feed stand-in).
3. Derive implied enterprise value: `closing_price_per_unit × total_units_across_all_tranches`.
4. Restate every tranche's carrying value against the new implied per-unit value.
5. Run 5 validation checks: price present/positive, arm's-length confirmed, IC approval present, uplift within a sane range vs. the weighted prior mark, units reconcile to the ledger record.
6. Return the confirmed valuation, matching §1.4 step 5's output shape.

On the Meridian golden path (tranche `MSC-T3` closing at $34.00/unit), this reproduces the mock dataset's own numbers exactly: implied total equity value $340,000,000, T1 restated to $153,000,000, T2 to $85,000,000, T3 at $102,000,000, +15.3% uplift vs. prior mark, 5/5 validation checks passed.

## Depends on

- [`mock-data`](../mock-data) — stand-in for the missing ledger DB and the customer price feed, installed as a path dependency.

## Tests

```bash
pip install -e ".[dev]"
pytest tests/ -v
```
