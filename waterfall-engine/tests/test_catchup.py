from waterfall_engine.models.fund import FundTerms
from waterfall_engine.models.state import WaterfallState
from waterfall_engine.rules.catchup import calculate_gp_catchup


def _state(distributable_cash: float, pref_paid: float, carry_percentage: float = 0.20) -> WaterfallState:
    fund = FundTerms(fund_id="F1", hurdle_rate=0.08, carry_percentage=carry_percentage)
    state = WaterfallState(
        fund=fund,
        contributed_capital_total=0,
        distributable_cash=distributable_cash,
    )
    state.pref_paid = pref_paid
    return state


def test_matches_golden_example_formula():
    # 8 pref, 20% carry, full catch-up -> catchup = 0.2/0.8 * 8 = 2
    state = calculate_gp_catchup(_state(distributable_cash=42, pref_paid=8))

    assert state.gp_catchup_paid == 2
    assert state.distributable_cash == 40


def test_capped_when_cash_insufficient():
    state = calculate_gp_catchup(_state(distributable_cash=1, pref_paid=8))

    assert state.gp_catchup_paid == 1
    assert state.distributable_cash == 0


def test_zero_when_carry_percentage_is_zero():
    state = calculate_gp_catchup(_state(distributable_cash=100, pref_paid=8, carry_percentage=0))

    assert state.gp_catchup_paid == 0
    assert state.distributable_cash == 100
