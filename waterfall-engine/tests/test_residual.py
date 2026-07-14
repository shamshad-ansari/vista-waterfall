from waterfall_engine.models.fund import FundTerms
from waterfall_engine.models.state import WaterfallState
from waterfall_engine.rules.residual import calculate_residual_split


def _state(distributable_cash: float, carry_percentage: float = 0.20) -> WaterfallState:
    fund = FundTerms(fund_id="F1", hurdle_rate=0.08, carry_percentage=carry_percentage)
    return WaterfallState(
        fund=fund,
        contributed_capital_total=0,
        distributable_cash=distributable_cash,
    )


def test_eighty_twenty_split():
    state = calculate_residual_split(_state(distributable_cash=40))

    assert state.lp_residual_paid == 32
    assert state.gp_residual_paid == 8
    assert state.distributable_cash == 0
    assert len(state.explanations) == 2


def test_cash_exhausted_both_sides_zero():
    state = calculate_residual_split(_state(distributable_cash=0))

    assert state.lp_residual_paid == 0
    assert state.gp_residual_paid == 0
    assert state.distributable_cash == 0
