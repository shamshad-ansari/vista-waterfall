from waterfall_engine.models.state import (
    WaterfallInput,
    WaterfallState,
    construct_initial_state,
)
from waterfall_engine.rules.catchup import calculate_gp_catchup
from waterfall_engine.rules.preferred_return import (
    accrue_preferred_return,
    pay_preferred_return,
)
from waterfall_engine.rules.residual import calculate_residual_split
from waterfall_engine.rules.return_of_capital import calculate_return_of_capital
from waterfall_engine.validators.validator import validate_input


def run_waterfall(input: WaterfallInput) -> WaterfallState:
    """Run the full pooled tier sequence and return the final state."""
    validate_input(input)
    state = construct_initial_state(input)
    state = calculate_return_of_capital(state)
    state = accrue_preferred_return(state, input.tranches, input.realization_date)
    state = pay_preferred_return(state)
    state = calculate_gp_catchup(state)
    state = calculate_residual_split(state)
    return state
