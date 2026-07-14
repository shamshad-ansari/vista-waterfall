from datetime import date

import pytest

from waterfall_engine.engine.allocation import allocate_lp_distributions
from waterfall_engine.engine.waterfall_engine import run_waterfall
from waterfall_engine.models.fund import FundTerms
from waterfall_engine.models.lp import LPCommitment
from waterfall_engine.models.state import WaterfallInput
from waterfall_engine.models.tranche import InvestmentTranche

# mock_datasets_Final_12pm.md §2.1-2.7 — Meridian Software Group, fund AGF3-2018.
MERIDIAN_TRANCHES = [
    InvestmentTranche(tranche_id="T1", amount=58_500_000, investment_date=date(2019, 3, 15)),
    InvestmentTranche(tranche_id="T2", amount=47_500_000, investment_date=date(2020, 8, 20)),
    InvestmentTranche(tranche_id="T3", amount=102_000_000, investment_date=date(2026, 6, 1)),
]
MERIDIAN_DISTRIBUTABLE_CASH = 340_000_000
MERIDIAN_REALIZATION_DATE = date(2026, 6, 1)

MERIDIAN_LP_ROSTER = [
    LPCommitment(lp_id="LP-001", lp_name="LP-001", commitment_amount=75_000_000),
    LPCommitment(lp_id="LP-002", lp_name="LP-002", commitment_amount=50_000_000),
    LPCommitment(lp_id="LP-003", lp_name="LP-003", commitment_amount=100_000_000),
    LPCommitment(lp_id="LP-004", lp_name="LP-004", commitment_amount=25_000_000),
    LPCommitment(lp_id="LP-005", lp_name="LP-005", commitment_amount=50_000_000),
    LPCommitment(lp_id="LP-006", lp_name="LP-006", commitment_amount=30_000_000),
    LPCommitment(lp_id="LP-007", lp_name="LP-007", commitment_amount=25_000_000),
    LPCommitment(lp_id="LP-008", lp_name="LP-008", commitment_amount=40_000_000),
    LPCommitment(lp_id="LP-009", lp_name="LP-009", commitment_amount=30_000_000),
    LPCommitment(lp_id="LP-010", lp_name="LP-010", commitment_amount=25_000_000),
]

# The doc's own worked example (§2.4) hand-rounds each tranche's hold period to
# 2 decimal places (7.21 / 5.78 years) before computing pref, whereas this engine
# uses the full-precision actual/365 day count per PLAN.md's formula. That
# truncation compounds across $58.5M/$47.5M of principal into a ~$60K gap on
# pref (and the residual/catch-up tiers derived from it) - bigger than a single
# rounding cent, but still a rounding-methodology artifact, not a logic bug (see
# the reconciliation invariants below, which hold exactly regardless).
TOLERANCE = 100_000


def _run_meridian():
    fund = FundTerms(fund_id="AGF3-2018", hurdle_rate=0.08, carry_percentage=0.20)
    input = WaterfallInput(
        fund=fund,
        tranches=MERIDIAN_TRANCHES,
        distributable_cash=MERIDIAN_DISTRIBUTABLE_CASH,
        realization_date=MERIDIAN_REALIZATION_DATE,
    )
    return run_waterfall(input)


def test_meridian_reconciles_to_invariants_not_bit_exact_figures():
    """Full run_waterfall() against the real Meridian dataset.

    This is an invariant/tolerance test, not a bit-exact one: the mock
    dataset's own worked example rounds the total pref mid-calculation
    ($55,705,000 -> $55,700,000) and cascades that rounding into the
    downstream catch-up/residual math. This engine deliberately keeps
    full precision internally and only rounds at display time, so its
    tier amounts are close to but not identical to the doc's figures.
    """
    state = _run_meridian()

    assert state.lp_total + state.gp_total == pytest.approx(MERIDIAN_DISTRIBUTABLE_CASH)

    profit_split = (state.lp_total - state.contributed_capital_total) / (
        MERIDIAN_DISTRIBUTABLE_CASH - state.contributed_capital_total
    )
    assert profit_split == pytest.approx(0.80)

    assert state.returned_capital == pytest.approx(208_000_000, abs=TOLERANCE)
    assert state.pref_paid == pytest.approx(55_700_000, abs=TOLERANCE)
    assert state.gp_catchup_paid == pytest.approx(13_900_000, abs=TOLERANCE)
    assert state.lp_residual_paid == pytest.approx(49_900_000, abs=TOLERANCE)
    assert state.gp_residual_paid == pytest.approx(12_500_000, abs=TOLERANCE)


def test_meridian_lp_allocation_matches_roster_split():
    state = _run_meridian()

    allocations = allocate_lp_distributions(state.lp_total, MERIDIAN_LP_ROSTER)

    assert sum(a.amount for a in allocations) == pytest.approx(state.lp_total)

    lp_003 = next(a for a in allocations if a.lp_id == "LP-003")
    assert lp_003.amount == pytest.approx(69_700_000, abs=TOLERANCE)
