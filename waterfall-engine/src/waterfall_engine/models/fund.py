from typing import Literal

from pydantic import BaseModel


class FundTerms(BaseModel):
    fund_id: str
    hurdle_rate: float
    carry_percentage: float
    catchup_percentage: float = 1.0
    preferred_return_compounding: Literal["simple"] = "simple"
    waterfall_type: Literal["american_deal_by_deal"] = "american_deal_by_deal"
