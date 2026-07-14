# Waterfall Calculation Engine — `waterfall-engine/` package

## Context

We're building the calculation logic behind the "Waterfall Agent" node of a 24-hour hackathon demo ("Composable Exit Orchestration"). The user owns two MCP servers in this repo — `valuation/` (Valuation Agent) and `waterfall-scenario/` (Waterfall Agent) — but neither currently does real math; both return hardcoded constants.

The authoritative source of truth for this plan is **`mock_datasets_Final_12pm.md`** (repo root), Stage 2 ("Waterfall Agent") in particular. It superseded two assumptions from earlier drafts of this plan:

- **Waterfall type is American / deal-by-deal, not European whole-fund.** The mock data's fund rules (`waterfall_type: American — Deal-by-Deal`) and scenario note ("carry is calculated on this realized investment independently, not against the whole fund's unreturned capital") make this explicit. Functionally this barely changes the tier math for a single-exit-event engine — the real implication is just that there's no cross-deal/whole-fund aggregation to build, which was already out of scope.
- **There is no per-LP balance tracking through the tiers.** Tiers 1–4 (return of capital → pref → GP catch-up → residual split) run once, on **pooled, deal-level scalars**: one `contributed_capital_total` ($208M across the investment's own 3 tranches), one `distributable_cash` ($340M), one blended pref figure (summed per investment-tranche, by hold period). LPs don't appear until a **separate, final step**: the resulting LP-tier-total is split pro-rata across the 10 LPs by each LP's **fund-wide commitment %** — unrelated to anything about this specific deal. This replaces the earlier "multi-LP correctness" design (per-LP `LPBalance`, per-LP pro-rata shortfall handling inside every tier) with something much simpler: pooled math for the tiers, then one flat allocation pass at the end.
- **"Tranches" means the fund's own investment tranches into one portfolio company** (three purchase dates for Meridian: 2019-03-15, 2020-08-20, 2026-06-01), not per-LP contribution history. Pref accrual is per-investment-tranche (simple interest, hold period from that tranche's date to the realization date), summed to one total — not per-LP.
- **Rounding**: internal math stays at full precision throughout (no mid-calculation rounding). Rounding to whole/display-friendly dollars is a presentation concern applied *outside* the engine (wherever results are shown), never inside `run_waterfall()` or the allocation step. This matters because the mock dataset's own worked example rounds the total pref ($55,705,000 → $55,700,000) and then uses that *rounded* figure in the downstream catch-up/residual math — i.e. its "golden" numbers aren't internally bit-exact to the last dollar. We deliberately don't replicate that rounding-then-cascading behavior; the Meridian scenario is used as a **reconciliation/invariant test** (totals balance, profit split is exactly 80/20, tier amounts are close to the doc's figures) rather than a bit-exact one. The pptx's clean single-tranche example (100/8/2/32/8) remains the only bit-exact golden test, since it has no rounding ambiguity.
- **Fields present in the mock tool schemas but unused by the tier math** — `management_fee`, `clawback_provision`, `gp_commitment_pct`, `prior_distributions_this_investment` (always 0 in this scenario) — stay out of the engine's models entirely. This matches the standing decision (see `AGENTS`/prior discussion) to descope management fees, clawback, and recycling for the hackathon; there's no reason to carry unused fields into `FundTerms`.

**Package placement**: this repo uses one src-layout package per domain (`valuation/`, `waterfall-scenario/`, each with their own `pyproject.toml`). The engine is its own sibling package, `waterfall-engine/`, to be consumed later as a dependency by `waterfall-scenario-mcp` — same pattern as the existing `peak-contracts` dependency. That wiring itself is out of scope for this plan.

**Explainability**: the product spec states the system must *not* expose how it calculated anything externally — only a one-line summary is shown in the UI. The engine keeps rich per-tier detail internally (useful for tests/debugging and any future audit surface); nothing forces that out through the eventual MCP boundary.

**Golden test case** (pptx slides 11–12, hand-verified, bit-exact): LP contributes 100 (GP contributes 0), exit proceeds 150, pref 8%, carry 20%, full catch-up, 1 year hold →
Tier 1: LP +100, cash 50 → Tier 2: LP +8 pref, cash 42 → Tier 3: GP +2 catch-up (formula: `catchup = carry/(1-carry) × pref_paid` = `0.2/0.8 × 8` = 2), cash 40 → Tier 4: 80/20 split → LP +32, GP +8. **Final: LP total 140, GP total 10.**

**Reconciliation scenario** (mock dataset Stage 2, Meridian Software Group, `mock_datasets_Final_12pm.md` §2.1–2.7): fund AGF3-2018, hurdle 8% simple, carry 20%, full catch-up, 3 investment tranches ($58.5M / $47.5M / $102M dated 2019-03-15 / 2020-08-20 / 2026-06-01), distributable cash $340M, realization date 2026-06-01. Expect (approximately, per the rounding note above): return of capital $208M, pref ≈$55.7M, catch-up ≈$13.9M, LP residual ≈$49.9M, GP residual ≈$12.5M, **LP total ≈$313.6M, GP total ≈$26.4M**, exactly reconciling to $340M with an exact 80/20 profit split. Then a separate allocation pass splits the ≈$313.6M LP total across the 10-LP roster (§2.7) by commitment %, e.g. LP-003 ($100M commitment / 22.222%) ≈ $69.7M.

## Package layout

```
waterfall-engine/
├── pyproject.toml              # hatchling, src layout — mirrors valuation/pyproject.toml (pydantic>=2.0, python>=3.11)
├── README.md
├── src/waterfall_engine/
│   ├── __init__.py
│   ├── models/
│   │   ├── fund.py             # FundTerms
│   │   ├── tranche.py          # InvestmentTranche (deal-level capital-in events, not per-LP)
│   │   ├── lp.py                # LPCommitment (fund-wide roster, used only for the final split)
│   │   ├── state.py             # WaterfallState (scalar/pooled), AllocationExplanation, WaterfallInput, LPAllocation
│   ├── rules/
│   │   ├── return_of_capital.py    # calculate_return_of_capital(state) -> state
│   │   ├── preferred_return.py     # accrue_preferred_return(state, tranches, realization_date) -> state ; pay_preferred_return(state) -> state
│   │   ├── catchup.py              # calculate_gp_catchup(state) -> state
│   │   └── residual.py             # calculate_residual_split(state) -> state
│   ├── engine/
│   │   ├── allocation.py       # allocate_pro_rata(total, weights: dict[str,float]) -> dict[str,float]  (shared helper); allocate_lp_distributions(lp_total, commitments: list[LPCommitment]) -> list[LPAllocation]
│   │   └── waterfall_engine.py # run_waterfall(input: WaterfallInput) -> WaterfallState  (fixed tier order, orchestration only; deal-level, no LP roster involved)
│   └── validators/
│       └── validator.py        # validate_input(input) -> None, raises WaterfallValidationError
└── tests/
    ├── test_return_of_capital.py
    ├── test_preferred_return.py
    ├── test_catchup.py
    ├── test_residual.py
    ├── test_lp_allocation.py
    ├── test_golden_example.py
    └── test_meridian_reconciliation.py
```

## Core models (`models/`)

```python
# fund.py
class FundTerms(BaseModel):
    fund_id: str
    hurdle_rate: float                # e.g. 0.08
    carry_percentage: float           # e.g. 0.20
    catchup_percentage: float = 1.0   # 1.0 = full catch-up
    preferred_return_compounding: Literal["simple"] = "simple"      # only simple supported for hackathon
    waterfall_type: Literal["american_deal_by_deal"] = "american_deal_by_deal"   # only this type supported for hackathon

# tranche.py
class InvestmentTranche(BaseModel):
    tranche_id: str
    amount: float
    investment_date: date

# lp.py
class LPCommitment(BaseModel):
    lp_id: str
    lp_name: str
    commitment_amount: float

# state.py
class AllocationExplanation(BaseModel):
    tier: str
    participant: str          # "LP" or "GP" — pooled model has no per-LP participants until final split
    cash_before: float
    amount_paid: float
    cash_after: float
    reason: str

class WaterfallState(BaseModel):
    fund: FundTerms
    contributed_capital_total: float
    distributable_cash: float          # mutated tier by tier — remaining cash
    returned_capital: float = 0
    accrued_pref: float = 0
    pref_paid: float = 0
    gp_catchup_paid: float = 0
    lp_residual_paid: float = 0
    gp_residual_paid: float = 0
    explanations: list[AllocationExplanation] = []

    @property
    def lp_total(self) -> float:
        return self.returned_capital + self.pref_paid + self.lp_residual_paid

    @property
    def gp_total(self) -> float:
        return self.gp_catchup_paid + self.gp_residual_paid

class WaterfallInput(BaseModel):
    fund: FundTerms
    tranches: list[InvestmentTranche]
    distributable_cash: float
    realization_date: date

class LPAllocation(BaseModel):
    lp_id: str
    lp_name: str
    amount: float
```

Rule: **every rule function takes a `WaterfallState` and returns a `WaterfallState`** — never a dict or tuple. Explanations are appended onto `state.explanations`, not returned separately.

## Tier functions (`rules/`), in fixed order — all operate on pooled scalars, no per-LP loop

1. **`calculate_return_of_capital(state)`** — `pay_capital = min(cash, contributed_capital_total)`. Single pooled payment, no allocation needed at this stage (only one "participant," the deal, until the final LP split). Appends one explanation.
2. **`accrue_preferred_return(state, tranches, realization_date)`** — per investment tranche: `accrued = tranche.amount × hurdle_rate × time_fraction`, where `time_fraction` is the actual/365 day-count hold period (`(realization_date - tranche.investment_date).days / 365`, flat divisor, no leap-year adjustment) from that tranche's own date to the realization date. Summed across all tranches into `state.accrued_pref`. No cash movement — pure accrual. Signature takes `tranches` directly (not `state.lp_balances`) since this is deal-level, not LP-level.
3. **`pay_preferred_return(state)`** — `pay_pref = min(remaining_cash, accrued_pref)`. Pooled payment, one explanation.
4. **`calculate_gp_catchup(state)`** — full formula: `catchup_target = catchup_percentage × (carry_percentage/(1-carry_percentage) × pref_paid)`, so partial catch-up structures (`catchup_percentage < 1.0`) scale the target proportionally, collapsing to the standard full-catch-up formula when `catchup_percentage = 1.0`. `pay_catchup = min(remaining_cash, catchup_target)` — if cash is short, GP simply gets whatever remains and cash hits 0; no special-casing needed, tier 5 then naturally computes a 0/0 split on zero remaining cash. Verified against both the pptx golden example (8 pref → 2 catch-up at 20% carry) and the Meridian reconciliation scenario (≈$55.7M pref → ≈$13.9M catch-up).
5. **`calculate_residual_split(state)`** — splits remaining cash `(1 - carry_percentage)` to LP-total / `carry_percentage` to GP-total. Still pooled — no LP-level split happens here.

Shared helper `allocate_pro_rata(total, weights)` in `engine/allocation.py` is now used in exactly one place: `allocate_lp_distributions`, which splits `state.lp_total` across the LP roster by `commitment_amount` weight. Tiers 1–5 no longer need it, since there's nothing to pro-rate until LPs enter the picture.

**Rounding rule for `allocate_pro_rata`**: uses the **largest-remainder method** — compute each recipient's exact proportional share, floor to cents, then distribute the leftover pennies one at a time to whichever recipients have the largest fractional remainder. This guarantees the split always sums back exactly to `total` (no floating-point leakage), which is the one place in the engine where exact-sum correctness matters regardless of the "logic over bit-exact matching" testing stance (see `test_lp_allocation.py`).

**Money type**: all monetary fields are plain `float`, not `Decimal`. `Decimal` would be more correct for production financial code, but adds real complexity (pydantic/JSON serialization quirks) not justified for a 24-hour happy-path build, especially since exact bit-for-bit matching against reference numbers isn't the bar (see Context, rounding note). The largest-remainder method above is what keeps the one place that must sum exactly (LP allocation) correct regardless of float imprecision elsewhere.

## Final step: LP-level allocation (decoupled from the tier engine)

```python
def allocate_lp_distributions(lp_total: float, commitments: list[LPCommitment]) -> list[LPAllocation]:
    """Split the pooled LP-tier-total across the LP roster by commitment share."""
```

This is a separate pure function, not part of `run_waterfall()` — it takes only the final `lp_total` scalar and the fund-wide LP roster, and has no knowledge of tiers, cash, or dates. This mirrors the mock dataset's own structure (§2.5 computes pooled tier totals; §2.7 is an independent commitment-%-weighted split).

## Orchestration (`engine/waterfall_engine.py`)

```python
def run_waterfall(input: WaterfallInput) -> WaterfallState:
    """Run the full waterfall tier sequence and return the final pooled state."""
    validate_input(input)
    state = construct_initial_state(input)
    state = calculate_return_of_capital(state)
    state = accrue_preferred_return(state, input.tranches, input.realization_date)
    state = pay_preferred_return(state)
    state = calculate_gp_catchup(state)
    state = calculate_residual_split(state)
    return state
```

`construct_initial_state` lives in `models/state.py` — sums `input.tranches` into `contributed_capital_total`, sets `distributable_cash = input.distributable_cash`. No LP roster involved at this stage.

## Validation (`validators/validator.py`)

`validate_input(input: WaterfallInput) -> None` — happy-path-appropriate, not exhaustive:
- non-empty `tranches`, all tranche amounts > 0
- `distributable_cash >= 0` (zero allowed — matches the "zero cash → no-op" test case)
- `hurdle_rate >= 0` (no upper cap)
- `carry_percentage` in `[0, 1)` — strictly less than 1 to avoid a division-by-zero in the catch-up formula; 0 is allowed (the "no carry" edge case)
- `catchup_percentage` in `[0, 1]`

Raises a single `WaterfallValidationError`. A lightweight separate check in `allocate_lp_distributions` (or inline) ensures `commitments` is non-empty and all `commitment_amount > 0` before dividing.

## Tests

- **`test_return_of_capital.py`** — full payment; cash insufficient to cover full capital (partial pooled payment, no allocation needed); zero cash (no-op, no explanations).
- **`test_preferred_return.py`** — accrual formula for a single tranche and for 3 tranches with different investment dates (mirrors Meridian's T1/T2/T3); payment capped when cash is short.
- **`test_catchup.py`** — exact formula match against the golden example (8 pref, 20% carry → 2 catch-up); zero when cash insufficient; zero when `carry_percentage` is 0 ("no carry" edge case).
- **`test_residual.py`** — 80/20 pooled split; cash-exhausted case (both sides get 0).
- **`test_lp_allocation.py`** — `allocate_lp_distributions` against a synthetic 3+ LP roster, asserting the split sums back exactly to `lp_total` (no rounding leakage) and each LP's share matches its commitment %; separately, sanity-check against the mock dataset's 10-LP roster (§2.7 weights) for approximate correctness.
- **`test_golden_example.py`** — full `run_waterfall()` run against the pptx worked example; asserts LP total **140**, GP total **10**, bit-exact, and each intermediate tier amount (100 / 8 / 2 / 32 / 8).
- **`test_meridian_reconciliation.py`** — full `run_waterfall()` run against the Meridian inputs (§2.1–2.4); asserts *invariants* rather than bit-exact dollar figures: `lp_total + gp_total == distributable_cash`, profit split is exactly 80/20 `((lp_total - contributed_capital_total) / (distributable_cash - contributed_capital_total) == 0.80)`, and each tier amount is within a small tolerance (e.g. ±$5,000) of the doc's displayed figures — documenting why exact equality isn't expected (see Context, rounding note).

## Explicitly out of scope for this plan

- Wiring `run_waterfall()` / `allocate_lp_distributions()` into `waterfall-scenario-mcp`'s tool handler (`get_waterfall_scenario.py`) — deferred until the real dataset delivery mechanism (DB vs. JSON vs. direct tool calls per the mock spec) is confirmed.
- A loader/adapter from the team's incoming dataset (or the mock tool schemas in `mock_datasets_Final_12pm.md` §0.2) into `WaterfallInput` / `LPCommitment`.
- Multi-deal / whole-fund netting, clawback, carry escrow, management fees, recycling, prior-distributions-on-this-investment (always 0 in scope; would need a `returned_capital`/`accrued_pref` starting offset if ever nonzero).
- Rounding/display formatting — stays entirely outside the engine, applied wherever results are shown.

## Verification

- `cd waterfall-engine && pip install -e ".[dev]"` (or plain `pip install -e .` + `pip install pytest`), then `pytest tests/ -v`.
- Golden-example assertions must match the pptx figures exactly (100/8/2/32/8, totals 140/10).
- Meridian reconciliation assertions check invariants + tolerance, not exact equality (see rounding note above).
- Spot-check `allocate_lp_distributions` independently to confirm it sums back to `lp_total` (no rounding leakage) across an odd number of LPs (e.g. 3-way split of a non-round number).

## Status

`pyproject.toml` has been created. Implementation of models/rules/engine/tests has **not** started — paused here per request. Resume by working through the package layout above top to bottom.
