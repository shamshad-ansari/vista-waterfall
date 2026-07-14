from waterfall_engine.models.state import AllocationExplanation, WaterfallState


def calculate_return_of_capital(state: WaterfallState) -> WaterfallState:
    """Tier 1: return contributed capital to the LP before any profit is recognized."""
    cash_before = state.distributable_cash
    pay_capital = min(cash_before, state.contributed_capital_total)

    state.returned_capital = pay_capital
    state.distributable_cash = cash_before - pay_capital
    state.explanations.append(
        AllocationExplanation(
            tier="return_of_capital",
            participant="LP",
            cash_before=cash_before,
            amount_paid=pay_capital,
            cash_after=state.distributable_cash,
            reason=(
                f"Return of capital = min(cash={cash_before}, "
                f"contributed_capital_total={state.contributed_capital_total})"
            ),
        )
    )
    return state
