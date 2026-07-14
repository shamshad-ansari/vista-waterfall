"""Waterfall schemas.

Local pydantic models matching mock_datasets_Final_12pm.md §2.8's real
Waterfall Agent output shape. There is no external `peak_contracts` package —
it never existed in this repo's dependency closure — so this MCP owns its own
contract.
"""

from pydantic import BaseModel, ConfigDict, Field


class WaterfallInput(BaseModel):
    """Tool input: a confirmed exit valuation plus the identifiers needed to
    look up the rest (fund rules, investment tranches, LP roster) from
    `mock_data`.
    """

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    investment_id: str = Field(
        ...,
        min_length=1,
        description="Investment identifier to look up cashflows for, e.g. 'MSC-2019-047'.",
    )
    fund_id: str = Field(
        ...,
        min_length=1,
        description="Fund identifier to look up fund rules and the LP roster for, e.g. 'AGF3-2018'.",
    )
    distributable_cash: float = Field(
        ...,
        gt=0,
        description=(
            "Confirmed exit valuation for this realization event — the Valuation "
            "Agent's ValuationOutput.confirmed_total_valuation."
        ),
    )


class TierResults(BaseModel):
    """Pooled, deal-level tier amounts from the American/deal-by-deal waterfall."""

    model_config = ConfigDict(extra="forbid")

    return_of_capital: float
    preferred_return: float
    gp_catchup: float
    lp_residual: float
    gp_residual: float


class LPAllocation(BaseModel):
    """One LP's pro-rata share of the pooled LP-tier-total, by fund commitment %."""

    model_config = ConfigDict(extra="forbid")

    lp_id: str
    amount: float


class WaterfallOutput(BaseModel):
    """Draft distribution scenario returned to the orchestrator.

    Per AGENTS.md's HITL note, this is a *proposed* distribution — `status`
    stays "PENDING_HITL_APPROVAL" until a human GP verifies it downstream.
    """

    model_config = ConfigDict(extra="forbid")

    investment_id: str
    distributable_cash: float
    tier_results: TierResults
    lp_total: float
    gp_total: float
    lp_allocations: list[LPAllocation]
    status: str = "PENDING_HITL_APPROVAL"


__all__ = ["LPAllocation", "TierResults", "WaterfallInput", "WaterfallOutput"]
