from waterfall_engine.models.fund import FundTerms
from waterfall_engine.models.state import WaterfallState
from waterfall_engine.rules.return_of_capital import calculate_return_of_capital


def _state(distributable_cash: float, contributed_capital_total: float) -> WaterfallState:
    fund = FundTerms(fund_id="F1", hurdle_rate=0.08, carry_percentage=0.20)
    return WaterfallState(
        fund=fund,
        contributed_capital_total=contributed_capital_total,
        distributable_cash=distributable_cash,
    )


def test_full_payment_when_cash_exceeds_capital():
    state = calculate_return_of_capital(_state(150, 100))

    assert state.returned_capital == 100
    assert state.distributable_cash == 50
    assert len(state.explanations) == 1
    assert state.explanations[0].tier == "return_of_capital"


def test_partial_payment_when_cash_insufficient():
    state = calculate_return_of_capital(_state(60, 100))

    assert state.returned_capital == 60
    assert state.distributable_cash == 0


def test_zero_cash_is_noop():
    state = calculate_return_of_capital(_state(0, 100))

    assert state.returned_capital == 0
    assert state.distributable_cash == 0
    assert state.explanations[0].amount_paid == 0
