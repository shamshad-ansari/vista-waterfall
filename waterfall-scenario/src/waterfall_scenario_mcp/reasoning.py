"""Waterfall Agent reasoning: real tier engine + LP allocation, no scaffolding.

Implements mock_datasets_Final_12pm.md SS0.2/SS2 — reasons across Tool A (Fund
& Investor Static Tool, native — mock_data.get_fund_rules /
mock_data.get_lp_roster) and Tool B (Accounting Cashflows Tool, native —
mock_data.get_cashflows), then runs the pooled tier sequence and final LP
allocation from the waterfall_engine package.
"""

from mock_data.lookups import get_cashflows, get_fund_rules, get_lp_roster

from waterfall_engine.engine.allocation import allocate_lp_distributions
from waterfall_engine.engine.waterfall_engine import run_waterfall
from waterfall_engine.models.fund import FundTerms
from waterfall_engine.models.lp import LPCommitment
from waterfall_engine.models.state import WaterfallInput as EngineWaterfallInput
from waterfall_engine.models.tranche import InvestmentTranche

from waterfall_scenario_mcp.schemas.waterfall import (
    LPAllocation,
    TierResults,
    WaterfallInput,
    WaterfallOutput,
)


def compute_waterfall_scenario(payload: WaterfallInput) -> WaterfallOutput:
    """Run the Waterfall Agent's end-to-end reasoning for a single realization event."""

    fund_rules = get_fund_rules(payload.fund_id)
    cashflows = get_cashflows(payload.investment_id)
    lp_roster = get_lp_roster(payload.fund_id)

    fund = FundTerms(
        fund_id=fund_rules.fund_id,
        hurdle_rate=fund_rules.hurdle_rate,
        carry_percentage=fund_rules.carry_split_gp,
    )
    tranches = [
        InvestmentTranche(
            tranche_id=contribution.tranche_id,
            amount=contribution.amount,
            investment_date=contribution.date,
        )
        for contribution in cashflows.contributions
    ]

    engine_input = EngineWaterfallInput(
        fund=fund,
        tranches=tranches,
        distributable_cash=payload.distributable_cash,
        realization_date=cashflows.realization_date,
    )
    state = run_waterfall(engine_input)

    commitments = [
        LPCommitment(lp_id=lp.lp_id, lp_name=lp.lp_id, commitment_amount=lp.commitment_amount)
        for lp in lp_roster
    ]
    allocations = allocate_lp_distributions(state.lp_total, commitments)

    return WaterfallOutput(
        investment_id=payload.investment_id,
        distributable_cash=payload.distributable_cash,
        tier_results=TierResults(
            return_of_capital=state.returned_capital,
            preferred_return=state.pref_paid,
            gp_catchup=state.gp_catchup_paid,
            lp_residual=state.lp_residual_paid,
            gp_residual=state.gp_residual_paid,
        ),
        lp_total=state.lp_total,
        gp_total=state.gp_total,
        lp_allocations=[LPAllocation(lp_id=a.lp_id, amount=a.amount) for a in allocations],
        status="PENDING_HITL_APPROVAL",
    )
