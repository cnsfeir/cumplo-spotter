# pylint: disable=no-self-argument, no-member

from decimal import Decimal
from enum import Enum
from math import ceil
from typing import Any

from pydantic import BaseModel, Field, validator

from models.borrower import Borrower
from models.request_duration import FundingRequestDuration
from utils.constants import CUMPLO_BASE_URL
from utils.currency import format_currency


class FundingRequestExtraInformation(BaseModel):
    paid_funding_requests_count: int = Field(...)
    paid_in_time_percentage: Decimal = Field(...)
    supporting_documents: list[str] = Field(...)
    average_days_delinquent: int = Field(...)
    funding_requests_count: int = Field(...)
    total_amount_requested: int = Field(...)
    dicom: bool = Field(...)


class CumploCreditType(str, Enum):
    IRRIGATION = "irrigation"
    BALLOON = "balloon"
    INVOICE = "invoice"
    BULLET = "bullet"
    SIMPLE = "simple"


class CreditType(str, Enum):
    WORKING_CAPITAL = "WORKING CAPITAL"
    STATE_SUBSIDY = "STATE SUBSIDY"
    BULLET_LOAN = "BULLET LOAN"
    FACTORING = "FACTORING"


CREDIT_TYPE_TRANSLATIONS = {
    CumploCreditType.IRRIGATION: CreditType.STATE_SUBSIDY,
    CumploCreditType.SIMPLE: CreditType.WORKING_CAPITAL,
    CumploCreditType.BALLOON: CreditType.BULLET_LOAN,
    CumploCreditType.BULLET: CreditType.BULLET_LOAN,
    CumploCreditType.INVOICE: CreditType.FACTORING,
}


class Currency(str, Enum):
    CLP = "CLP"


class FundingRequest(BaseModel):
    id: int = Field(...)
    score: Decimal = Field(...)
    borrower: Borrower = Field(...)
    irr: Decimal = Field(..., alias="tir")
    currency: Currency = Field(..., alias="moneda")
    amount: int = Field(..., alias="monto_financiar")
    anual_profit_rate: Decimal = Field(..., alias="tasa_anual")
    duration: FundingRequestDuration = Field(..., alias="plazo")
    supporting_documents: list[str] = Field(default_factory=list)
    funded_amount_percentage: Decimal = Field(..., alias="porcentaje_inversion")
    credit_type: CreditType = Field(..., alias="tipo_respaldo", anystr_upper=True)

    @validator("funded_amount_percentage", pre=True)
    def funded_amount_percentage_validator(cls, value: Any) -> Decimal:
        """
        Validates that the funded_amount_percentage is a valid decimal number.
        If it is not, it returns None which means that it does not have a credit history yet.
        """
        try:
            return round(Decimal(int(value) / 100), 2)
        except ValueError:
            return Decimal(0)

    @validator("anual_profit_rate", pre=True)
    def anual_profit_rate_validator(cls, value: Any) -> Decimal:
        """Validates that the anual_profit_rate is a valid decimal number"""
        return round(Decimal(int(value) / 100), 2)

    @validator("credit_type", pre=True)
    def credit_type_validator(cls, value: Any) -> CreditType:
        """Validates that the credit_type has a valid value"""
        return CREDIT_TYPE_TRANSLATIONS[value]

    def __hash__(self) -> int:
        """Returns the hash of the funding request"""
        return hash(self.json())

    @property
    def is_completed(self) -> bool:
        """Checks if the funding request is fully funded"""
        return self.funded_amount_percentage == Decimal(1)

    @property
    def profit_rate(self) -> Decimal:
        """Calculates the profit rate for the funding request"""
        return (1 + self.irr / 100) ** Decimal(self.duration.value / 365) - 1

    @property
    def monthly_profit_rate(self) -> Decimal:
        """Calculates the monthly profit rate for the funding request"""
        return round(self.profit_rate * 30 / self.duration.value, 4)

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
            "monthly_profit_rate": self.monthly_profit_rate,
            "credit_type": self.credit_type,
            "amount": format_currency(self.amount),
            "url": self.url,
        }
