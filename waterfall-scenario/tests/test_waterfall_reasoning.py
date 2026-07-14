import pytest
from mock_data.lookups import UnknownFundError, UnknownInvestmentError

from waterfall_scenario_mcp.reasoning import compute_waterfall_scenario
from waterfall_scenario_mcp.schemas.waterfall import WaterfallInput

INVESTMENT_ID = "MSC-2019-047"
FUND_ID = "AGF3-2018"
CONFIRMED_VALUATION = 340_000_000

# mock_datasets_Final_12pm.md §2.5-2.8 — Meridian's own worked example rounds
# the total pref mid-calculation ($55,705,000 -> $55,700,000) and cascades that
# rounding into the downstream catch-up/residual math; this engine keeps full
# precision internally and only rounds at display time (per PLAN.md's
# rounding note), so figures are close to but not identical to the doc's.
# Matches waterfall-engine/tests/test_meridian_reconciliation.py's tolerance.
TOLERANCE = 100_000


def _run_meridian():
    payload = WaterfallInput(
        investment_id=INVESTMENT_ID,
        fund_id=FUND_ID,
        distributable_cash=CONFIRMED_VALUATION,
    )
    return compute_waterfall_scenario(payload)


def test_meridian_reconciles_to_doc_figures():
    result = _run_meridian()

    assert result.investment_id == INVESTMENT_ID
    assert result.distributable_cash == CONFIRMED_VALUATION
    assert result.status == "PENDING_HITL_APPROVAL"

    assert result.tier_results.return_of_capital == pytest.approx(208_000_000, abs=TOLERANCE)
    assert result.tier_results.preferred_return == pytest.approx(55_700_000, abs=TOLERANCE)
    assert result.tier_results.gp_catchup == pytest.approx(13_925_000, abs=TOLERANCE)
    assert result.tier_results.lp_residual == pytest.approx(49_900_000, abs=TOLERANCE)
    assert result.tier_results.gp_residual == pytest.approx(12_475_000, abs=TOLERANCE)

    assert result.lp_total == pytest.approx(313_600_000, abs=TOLERANCE)
    assert result.gp_total == pytest.approx(26_400_000, abs=TOLERANCE)
    assert result.lp_total + result.gp_total == pytest.approx(CONFIRMED_VALUATION)


def test_meridian_lp_allocations_match_roster_split():
    result = _run_meridian()

    assert {a.lp_id for a in result.lp_allocations} == {f"LP-{i:03d}" for i in range(1, 11)}
    assert sum(a.amount for a in result.lp_allocations) == pytest.approx(result.lp_total)

    lp_003 = next(a for a in result.lp_allocations if a.lp_id == "LP-003")
    assert lp_003.amount == pytest.approx(69_688_889, abs=TOLERANCE)

    # GP carry never appears in the LP allocation list — no "GP-001" row.
    assert all(a.lp_id.startswith("LP-") for a in result.lp_allocations)


def test_unknown_fund_id_raises():
    payload = WaterfallInput(
        investment_id=INVESTMENT_ID, fund_id="NOT-A-FUND", distributable_cash=CONFIRMED_VALUATION
    )
    with pytest.raises(UnknownFundError):
        compute_waterfall_scenario(payload)


def test_unknown_investment_id_raises():
    payload = WaterfallInput(
        investment_id="NOT-AN-INVESTMENT", fund_id=FUND_ID, distributable_cash=CONFIRMED_VALUATION
    )
    with pytest.raises(UnknownInvestmentError):
        compute_waterfall_scenario(payload)
