from datetime import date

from waterfall_engine.models.fund import FundTerms
from waterfall_engine.models.state import WaterfallState
from waterfall_engine.models.tranche import InvestmentTranche
from waterfall_engine.rules.preferred_return import (
    accrue_preferred_return,
    pay_preferred_return,
)


def _state(distributable_cash: float, hurdle_rate: float = 0.08) -> WaterfallState:
    fund = FundTerms(fund_id="F1", hurdle_rate=hurdle_rate, carry_percentage=0.20)
    return WaterfallState(
        fund=fund,
        contributed_capital_total=0,
        distributable_cash=distributable_cash,
    )


def test_single_tranche_accrual():
    state = _state(distributable_cash=1000)
    tranche = InvestmentTranche(
        tranche_id="T1", amount=100, investment_date=date(2019, 1, 1)
    )

    state = accrue_preferred_return(state, [tranche], date(2020, 1, 1))

    assert state.accrued_pref == 8  # 100 * 0.08 * (365/365)
    assert state.distributable_cash == 1000  # pure accrual, no cash movement


def test_multi_tranche_accrual_sums_across_tranches():
    state = _state(distributable_cash=1000)
    tranches = [
        InvestmentTranche(
            tranche_id="T1", amount=100, investment_date=date(2019, 1, 1)
        ),
        InvestmentTranche(
            tranche_id="T2", amount=200, investment_date=date(2019, 7, 1)
        ),
    ]
    realization_date = date(2020, 1, 1)

    state = accrue_preferred_return(state, tranches, realization_date)

    expected = sum(
        t.amount * state.fund.hurdle_rate * ((realization_date - t.investment_date).days / 365)
        for t in tranches
    )
    assert state.accrued_pref == expected


def test_payment_capped_when_cash_short():
    state = _state(distributable_cash=5)
    state.accrued_pref = 8

    state = pay_preferred_return(state)

    assert state.pref_paid == 5
    assert state.distributable_cash == 0


def test_payment_pays_full_accrual_when_cash_sufficient():
    state = _state(distributable_cash=50)
    state.accrued_pref = 8

    state = pay_preferred_return(state)

    assert state.pref_paid == 8
    assert state.distributable_cash == 42
