from datetime import date

from pydantic import BaseModel


class TrancheRecord(BaseModel):
    tranche_id: str
    investment_date: date
    ownership_acquired_pct: float
    cost_basis: float
    security_type: str
    units_held: float
    pricing_status: str
    cost_per_unit: float | None = None
    prior_mark_per_unit: float | None = None
    prior_carrying_value: float | None = None
    last_valuation_date: date | None = None
    closing_price_per_unit: float | None = None


class AssetRecord(BaseModel):
    asset_id: str
    asset_name: str
    asset_type: str
    sector: str
    region: str
    fund_id: str
    fund_name: str
    initial_investment_date: date
    current_ownership_pct: float
    prior_total_carrying_value: float
    valuation_status: str
    tranches: list[TrancheRecord]


class PriceFeedResponse(BaseModel):
    request_id: str
    asset_id: str
    tranche_id: str
    transaction_type: str
    closing_price_per_unit: float
    units_transacted: float
    total_transaction_value: float
    transaction_date: date
    counterparty: str
    methodology: str
    ic_approved_by: str
    arm_length_confirmation: bool


class FundRules(BaseModel):
    fund_id: str
    fund_name: str
    waterfall_type: str
    hurdle_rate: float
    catch_up_structure: str
    carry_split_lp: float
    carry_split_gp: float
    gp_commitment_pct: float
    total_commitments: float
    clawback_provision: str
    management_fee: str


class LPCommitment(BaseModel):
    lp_id: str
    commitment_amount: float
    ownership_pct: float


class TrancheContribution(BaseModel):
    tranche_id: str
    amount: float
    date: date


class CashflowRecord(BaseModel):
    investment_id: str
    contributed_capital_total: float
    contributions: list[TrancheContribution]
    prior_distributions_this_investment: float
    realization_date: date
