from pydantic import BaseModel, ConfigDict, Field


class ValuationInput(BaseModel):
    """Input for asset valuation (scaffold — values are hardcoded for now)."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    closing_price: float = Field(
        ...,
        gt=0,
        description="Closing price of the position used to derive asset valuation.",
    )
    position_id: str = Field(
        default="POS-001",
        min_length=1,
        max_length=64,
        description="Identifier for the position being valued.",
    )


class ValuationOutput(BaseModel):
    """Structured valuation result returned to agents."""

    model_config = ConfigDict(extra="forbid")

    position_id: str = Field(..., description="Position that was valued.")
    closing_price: float = Field(..., gt=0, description="Closing price used in the calculation.")
    asset_valuation: float = Field(..., gt=0, description="Computed valuation of the underlying asset.")
    currency: str = Field(default="USD", description="Currency of monetary values.")
    valuation_method: str = Field(
        default="hardcoded_scaffold",
        description="Method used to compute the valuation.",
    )
