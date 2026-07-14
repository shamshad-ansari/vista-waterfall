from pydantic import BaseModel


class LPCommitment(BaseModel):
    lp_id: str
    lp_name: str
    commitment_amount: float
