from datetime import date

from waterfall_engine.models.state import AllocationExplanation, WaterfallState
from waterfall_engine.models.tranche import InvestmentTranche


def accrue_preferred_return(
    state: WaterfallState,
    tranches: list[InvestmentTranche],
    realization_date: date,
) -> WaterfallState:
    """Tier 2a: accrue simple-interest preferred return per investment tranche.

    Pure accrual — no cash movement. Summed across tranches into
    `state.accrued_pref`.
    """
    cash_before = state.distributable_cash
    total_accrued = 0.0
    for tranche in tranches:
        time_fraction = (realization_date - tranche.investment_date).days / 365
        total_accrued += tranche.amount * state.fund.hurdle_rate * time_fraction

    state.accrued_pref = total_accrued
    state.explanations.append(
        AllocationExplanation(
            tier="preferred_return_accrual",
            participant="LP",
            cash_before=cash_before,
            amount_paid=total_accrued,
            cash_after=cash_before,
            reason=(
                f"Accrued preferred return across {len(tranches)} tranche(s) at "
                f"hurdle_rate={state.fund.hurdle_rate} through {realization_date}"
            ),
        )
    )
    return state


def pay_preferred_return(state: WaterfallState) -> WaterfallState:
    """Tier 2b: pay accrued preferred return out of remaining cash."""
    cash_before = state.distributable_cash
    pay_pref = min(cash_before, state.accrued_pref)

    state.pref_paid = pay_pref
    state.distributable_cash = cash_before - pay_pref
    state.explanations.append(
        AllocationExplanation(
            tier="preferred_return_payment",
            participant="LP",
            cash_before=cash_before,
            amount_paid=pay_pref,
            cash_after=state.distributable_cash,
            reason=(
                f"Preferred return payment = min(cash={cash_before}, "
                f"accrued_pref={state.accrued_pref})"
            ),
        )
    )
    return state
