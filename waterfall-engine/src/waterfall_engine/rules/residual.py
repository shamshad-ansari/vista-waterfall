from waterfall_engine.models.state import AllocationExplanation, WaterfallState


def calculate_residual_split(state: WaterfallState) -> WaterfallState:
    """Tier 4: split remaining cash (1 - carry) to LP / carry to GP."""
    cash_before = state.distributable_cash
    carry = state.fund.carry_percentage
    lp_share = cash_before * (1 - carry)
    gp_share = cash_before * carry

    state.lp_residual_paid = lp_share
    state.gp_residual_paid = gp_share
    state.distributable_cash = 0

    state.explanations.append(
        AllocationExplanation(
            tier="residual_split",
            participant="LP",
            cash_before=cash_before,
            amount_paid=lp_share,
            cash_after=state.distributable_cash,
            reason=f"Residual split = cash={cash_before} * (1 - carry_percentage={carry})",
        )
    )
    state.explanations.append(
        AllocationExplanation(
            tier="residual_split",
            participant="GP",
            cash_before=cash_before,
            amount_paid=gp_share,
            cash_after=state.distributable_cash,
            reason=f"Residual split = cash={cash_before} * carry_percentage={carry}",
        )
    )
    return state
