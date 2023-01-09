# pylint: disable=no-member

from enum import Enum
from math import ceil

from pydantic import BaseModel, Field

from models.borrower import Borrower
from models.payer import Institution
from models.request_duration import FundingRequestDuration


class CreditType(str, Enum):
    INVOICE = "invoice"
    IRRIGATION = "irrigation"


class FundingRequest(BaseModel):
    id: int = Field(...)
    tir: float = Field(...)
    amount: int = Field(...)
    score: float = Field(..., alias="dac")
    duration: FundingRequestDuration = Field(...)
    credit_type: str = Field(..., alias="creditType")
    borrower: Borrower = Field(..., alias="requestable")
    funded_amount: int = Field(..., alias="fundedAmount")
    institution: Institution = Field(..., alias="outstandingPayer")

    @property
    def is_completed(self) -> bool:
        """Checks if the funding request is fully funded"""
        return self.amount == self.funded_amount

    @property
    def profit_rate(self) -> float:
        """Calculates the profit rate for the funding request"""
        return ((1 + self.tir / 100) ** (self.duration.value / 365)) - 1

    @property
    def monthly_profit_rate(self) -> float:
        """Calculates the monthly profit rate for the funding request"""
        return round(self.profit_rate * 30 / self.duration.value, 4)

    def monthly_profit(self, amount: int) -> int:
        """Calculates the monthly profit for a given amount"""
        return ceil(self.monthly_profit_rate * amount)

    def serialized(self) -> dict:
        """
        Serializes the funding request to a dictionary
        """
        return {"monthly_profit_rate": self.monthly_profit_rate, **self.dict()}
