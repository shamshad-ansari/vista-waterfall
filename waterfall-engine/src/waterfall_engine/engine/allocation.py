import math

from waterfall_engine.models.lp import LPCommitment
from waterfall_engine.models.state import LPAllocation
from waterfall_engine.validators.validator import WaterfallValidationError


def allocate_pro_rata(total: float, weights: dict[str, float]) -> dict[str, float]:
    """Split `total` across `weights` using the largest-remainder method.

    Guarantees the result sums back exactly to `total` (to the cent),
    regardless of float imprecision in the proportional shares.
    """
    if not weights:
        raise WaterfallValidationError("weights must be non-empty")

    total_weight = sum(weights.values())
    total_cents = round(total * 100)

    floor_cents: dict[str, int] = {}
    remainders: dict[str, float] = {}
    allocated_cents = 0
    for key, weight in weights.items():
        exact_cents = total_cents * weight / total_weight
        floor = math.floor(exact_cents)
        floor_cents[key] = floor
        remainders[key] = exact_cents - floor
        allocated_cents += floor

    leftover_cents = total_cents - allocated_cents
    for key in sorted(remainders, key=lambda k: remainders[k], reverse=True)[:leftover_cents]:
        floor_cents[key] += 1

    return {key: cents / 100 for key, cents in floor_cents.items()}


def allocate_lp_distributions(
    lp_total: float, commitments: list[LPCommitment]
) -> list[LPAllocation]:
    """Split the pooled LP-tier-total across the LP roster by commitment share."""
    if not commitments:
        raise WaterfallValidationError("commitments must be non-empty")
    for commitment in commitments:
        if commitment.commitment_amount <= 0:
            raise WaterfallValidationError(
                f"LP '{commitment.lp_id}' commitment_amount must be > 0, "
                f"got {commitment.commitment_amount}"
            )

    weights = {c.lp_id: c.commitment_amount for c in commitments}
    amounts = allocate_pro_rata(lp_total, weights)

    return [
        LPAllocation(lp_id=c.lp_id, lp_name=c.lp_name, amount=amounts[c.lp_id])
        for c in commitments
    ]
