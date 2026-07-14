from datetime import date

from pydantic import BaseModel


class InvestmentTranche(BaseModel):
    tranche_id: str
    amount: float
    investment_date: date
