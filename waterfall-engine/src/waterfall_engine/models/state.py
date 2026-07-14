from datetime import date

from pydantic import BaseModel, Field

from waterfall_engine.models.fund import FundTerms
from waterfall_engine.models.tranche import InvestmentTranche


class AllocationExplanation(BaseModel):
    tier: str
    participant: str  # "LP" or "GP" — pooled model has no per-LP participants until final split
    cash_before: float
    amount_paid: float
    cash_after: float
    reason: str


class WaterfallState(BaseModel):
    fund: FundTerms
    contributed_capital_total: float
    distributable_cash: float  # mutated tier by tier — remaining cash
    returned_capital: float = 0
    accrued_pref: float = 0
    pref_paid: float = 0
    gp_catchup_paid: float = 0
    lp_residual_paid: float = 0
    gp_residual_paid: float = 0
    explanations: list[AllocationExplanation] = Field(default_factory=list)

    @property
    def lp_total(self) -> float:
        return self.returned_capital + self.pref_paid + self.lp_residual_paid

    @property
    def gp_total(self) -> float:
        return self.gp_catchup_paid + self.gp_residual_paid


class WaterfallInput(BaseModel):
    fund: FundTerms
    tranches: list[InvestmentTranche]
    distributable_cash: float
    realization_date: date


class LPAllocation(BaseModel):
    lp_id: str
    lp_name: str
    amount: float


def construct_initial_state(input: WaterfallInput) -> WaterfallState:
    """Build the zeroed pooled state that the tier sequence runs against."""
    return WaterfallState(
        fund=input.fund,
        contributed_capital_total=sum(t.amount for t in input.tranches),
        distributable_cash=input.distributable_cash,
    )
