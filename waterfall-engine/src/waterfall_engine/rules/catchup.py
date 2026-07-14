from waterfall_engine.models.state import AllocationExplanation, WaterfallState


def calculate_gp_catchup(state: WaterfallState) -> WaterfallState:
    """Tier 3: GP catch-up, scaled by `catchup_percentage` (1.0 = full catch-up)."""
    cash_before = state.distributable_cash
    carry = state.fund.carry_percentage
    full_catchup = (carry / (1 - carry)) * state.pref_paid
    catchup_target = state.fund.catchup_percentage * full_catchup
    pay_catchup = min(cash_before, catchup_target)

    state.gp_catchup_paid = pay_catchup
    state.distributable_cash = cash_before - pay_catchup
    state.explanations.append(
        AllocationExplanation(
            tier="gp_catchup",
            participant="GP",
            cash_before=cash_before,
            amount_paid=pay_catchup,
            cash_after=state.distributable_cash,
            reason=(
                f"GP catch-up = min(cash={cash_before}, catchup_percentage="
                f"{state.fund.catchup_percentage} * carry/(1-carry) * pref_paid="
                f"{catchup_target})"
            ),
        )
    )
    return state
