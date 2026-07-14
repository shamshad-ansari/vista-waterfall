from waterfall_engine.models.state import WaterfallInput


class WaterfallValidationError(ValueError):
    """Raised when a WaterfallInput fails happy-path validation."""


def validate_input(input: WaterfallInput) -> None:
    """Happy-path validation — not exhaustive, see waterfall-engine/PLAN.md."""
    if not input.tranches:
        raise WaterfallValidationError("tranches must be non-empty")
    for tranche in input.tranches:
        if tranche.amount <= 0:
            raise WaterfallValidationError(
                f"tranche '{tranche.tranche_id}' amount must be > 0, got {tranche.amount}"
            )

    if input.distributable_cash < 0:
        raise WaterfallValidationError(
            f"distributable_cash must be >= 0, got {input.distributable_cash}"
        )

    if input.fund.hurdle_rate < 0:
        raise WaterfallValidationError(
            f"hurdle_rate must be >= 0, got {input.fund.hurdle_rate}"
        )

    if not (0 <= input.fund.carry_percentage < 1):
        raise WaterfallValidationError(
            f"carry_percentage must be in [0, 1), got {input.fund.carry_percentage}"
        )

    if not (0 <= input.fund.catchup_percentage <= 1):
        raise WaterfallValidationError(
            f"catchup_percentage must be in [0, 1], got {input.fund.catchup_percentage}"
        )
