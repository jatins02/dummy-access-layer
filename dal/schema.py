"""
Step 1: the closed vocabulary. The model may only produce a Proposal.
"""
from decimal import Decimal     # fast, correctly rounded and arbitrary-precision decimal floating point arithmetic.
from typing import Literal, Optional
from pydantic import BaseModel, ConfigDict, Field, model_validator


class Proposal(BaseModel):
    model_config = ConfigDict(extra="forbid")  # unknown fields are rejected
    action: Literal["balance", "send", "clarify"]   # no arbitrary actions other than these, somehow add new action in this, vulnerability
    to: Optional[str] = Field(default=None, max_length=64)
    amount_eth: Optional[Decimal] = Field(default=None, gt=0, max_digits=20, decimal_places=18)
    question: Optional[str] = Field(default=None, max_length=200)

    @model_validator(mode="after")  # runs after the above test pass
    def send_needs_fields(self):
        if self.action == "send" and (self.to is None or self.amount_eth is None):
            raise ValueError("send requires 'to' and 'amount_eth'")
        return self
