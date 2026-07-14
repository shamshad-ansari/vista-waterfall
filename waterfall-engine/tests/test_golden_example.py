from datetime import date

from waterfall_engine.engine.waterfall_engine import run_waterfall
from waterfall_engine.models.fund import FundTerms
from waterfall_engine.models.state import WaterfallInput
from waterfall_engine.models.tranche import InvestmentTranche


def test_pptx_golden_example():
    """LP 100 / proceeds 150 / pref 8% / carry 20% / full catch-up / 1yr hold.

    Expected tier amounts: 100 / 8 / 2 / 32 / 8. LP total 140, GP total 10.
    """
    fund = FundTerms(fund_id="GOLDEN", hurdle_rate=0.08, carry_percentage=0.20)
    tranches = [
        InvestmentTranche(
            tranche_id="T1", amount=100, investment_date=date(2019, 1, 1)
        )
    ]
    input = WaterfallInput(
        fund=fund,
        tranches=tranches,
        distributable_cash=150,
        realization_date=date(2020, 1, 1),
    )

    state = run_waterfall(input)

    assert state.returned_capital == 100
    assert state.pref_paid == 8
    assert state.gp_catchup_paid == 2
    assert state.lp_residual_paid == 32
    assert state.gp_residual_paid == 8

    assert state.lp_total == 140
    assert state.gp_total == 10
    assert state.distributable_cash == 0
