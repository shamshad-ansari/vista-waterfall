from datetime import date

from pydantic import BaseModel, ConfigDict, Field


class ValuationInput(BaseModel):
    """Input for the Valuation Agent's reasoning over an asset's tranches.

    Mirrors what Tool B (the customer-registered Price Feed Tool) would hand
    back for the unpriced tranche. If the price-feed fields are omitted, the
    tool falls back to `mock_data.get_price_feed_response` as the demo
    stand-in for that external call.
    """

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    asset_id: str = Field(
        ...,
        min_length=1,
        description="Asset identifier to load from the ledger (Tool A stand-in), e.g. 'MSC-2019-047'.",
    )
    closing_price_per_unit: float | None = Field(
        default=None,
        gt=0,
        description="Closing/transaction price per unit for the unpriced tranche, from the price feed.",
    )
    methodology: str | None = Field(
        default=None,
        description="Pricing methodology used, e.g. 'negotiated_transaction_price'.",
    )
    ic_approved_by: str | None = Field(
        default=None,
        description="Investment Committee approval reference for the transaction.",
    )
    effective_date: date | None = Field(
        default=None,
        description="Date the new price became effective.",
    )
    arm_length_confirmation: bool | None = Field(
        default=None,
        description="Whether the transaction was confirmed arm's-length.",
    )


class ValidationCheck(BaseModel):
    """Result of a single validation check the agent runs before confirming a valuation."""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(..., description="Name of the check.")
    passed: bool = Field(..., description="Whether the check passed.")
    detail: str = Field(..., description="Human-readable detail on the check outcome.")


class ValuationOutput(BaseModel):
    """Confirmed valuation result returned to the orchestrator."""

    model_config = ConfigDict(extra="forbid")

    asset_id: str = Field(..., description="Asset that was valued.")
    confirmed_total_valuation: float = Field(..., description="Implied total enterprise/equity value.")
    valuation_per_unit: float = Field(..., gt=0, description="New per-unit value used to restate all tranches.")
    methodology: str = Field(..., description="Valuation methodology used.")
    effective_date: date = Field(..., description="Date the confirmed valuation is effective.")
    tranche_values: dict[str, float] = Field(
        ..., description="Restated carrying value per tranche_id, including the newly priced tranche."
    )
    prior_total_carrying_value: float = Field(
        ..., description="Sum of prior carrying values across previously priced tranches."
    )
    valuation_uplift: float = Field(
        ..., description="Dollar change: confirmed_total_valuation minus prior_total_carrying_value."
    )
    validation_status: str = Field(..., description="e.g. 'PASSED — 5 of 5 checks' or which checks failed.")
    validation_checks: list[ValidationCheck] = Field(
        default_factory=list, description="Individual validation check results."
    )
    source_tool: str = Field(
        default="Acme Price Feed (customer-registered)",
        description="Name of the price feed tool that supplied the new price.",
    )
