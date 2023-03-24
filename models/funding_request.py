# pylint: disable=no-self-argument, no-member

from decimal import Decimal
from enum import Enum
from math import ceil
from typing import Any

from pydantic import BaseModel, Field, validator

from models.borrower import Borrower
from models.payer import Institution
from models.request_duration import FundingRequestDuration
from utils.currency import format_currency

CUMPLO_BASE_URL = "https://secure.cumplo.cl"


class FundingRequestExtraInformation(BaseModel):
    paid_in_time_percentage: Decimal = Field(...)
    supporting_documents: list[str] = Field(...)
    average_days_delinquent: int = Field(...)
    dicom: bool = Field(...)

    @validator("paid_in_time_percentage", pre=True)
    def paid_in_time_validator(cls, value: Any) -> Decimal:
        """
        Validates that the paid_on_time is a valid decimal number.
        If it is not, it returns None which means that it does not have a credit history yet.
        """
        try:
            return round(Decimal(int(value) / 100), 3)
        except ValueError:
            return Decimal(0)


class CreditType(str, Enum):
    IRRIGATION = "irrigation"
    BALLOON = "balloon"
    INVOICE = "invoice"
    SIMPLE = "simple"


class FundingRequest(BaseModel):
    id: int = Field(...)
    amount: int = Field(...)
    irr: Decimal = Field(..., alias="tir")
    score: Decimal = Field(..., alias="dac")
    duration: FundingRequestDuration = Field(...)
    borrower: Borrower = Field(..., alias="requestable")
    funded_amount: int = Field(..., alias="fundedAmount")
    supporting_documents: list[str] = Field(default_factory=list)
    institution: Institution = Field(..., alias="outstandingPayer")
    credit_type: CreditType = Field(..., alias="creditType", anystr_upper=True)

    @property
    def is_completed(self) -> bool:
        """Checks if the funding request is fully funded"""
        return self.amount == self.funded_amount

    @property
    def profit_rate(self) -> Decimal:
        """Calculates the profit rate for the funding request"""
        return (1 + self.irr / 100) ** Decimal(self.duration.value / 365) - 1

    @property
    def monthly_profit_rate(self) -> Decimal:
        """Calculates the monthly profit rate for the funding request"""
        return round(self.profit_rate * 30 / self.duration.value, 4)

    @property
    def funded_amount_percentage(self) -> Decimal:
        """Calculates the monthly profit rate for the funding request"""
        return round(Decimal(self.funded_amount / self.amount), 4)

    @property
    def url(self) -> str:
        """Builds the URL for the funding request"""
        return f"{CUMPLO_BASE_URL}/{self.id}"

    def monthly_profit(self, amount: int) -> int:
        """Calculates the monthly profit for a given amount"""
        return ceil(self.monthly_profit_rate * amount)

    def dict(self, *args: Any, **kwargs: Any) -> dict:
        """Builds a dictionary with the funding request data"""
        return {
            **super().dict(*args, **kwargs),
            "funded_amount_percentage": self.funded_amount_percentage,
            "funded_amount": format_currency(self.funded_amount),
            "monthly_profit_rate": self.monthly_profit_rate,
            "credit_type": self.credit_type.upper(),
            "amount": format_currency(self.amount),
            "url": self.url,
        }
