# pylint: disable=no-self-argument, no-member

from logging import getLogger
from typing import Any

from babel.numbers import format_currency
from pydantic import BaseModel, Field, validator

logger = getLogger(__name__)


class CreditHistory(BaseModel):
    dicom: bool = Field(...)
    average_deliquent_days: int = Field(...)
    paid_in_time: float = Field(...)

    @validator("paid_in_time", pre=True)
    def paid_in_time_validator(cls, value: Any) -> float:
        """
        Validates that the paid_on_time is a int.
        If it is not, it returns None which means that it does not have a credit history yet.
        """
        try:
            return float(int(value) / 100)
        except ValueError:
            return float(0.0)


class Borrower(BaseModel):
    id: str = Field(...)
    name: str | None = Field(None)
    fantasy_name: str = Field(..., alias="fantasyName")
    total_requested: int = Field(..., alias="instalmentsCapital")
    funding_requests_count: int = Field(..., alias="fundingRequestsCount")
    funding_requests_paid_count: int = Field(..., alias="fundingRequestsPaidCount")
    instalments_paid_in_time: int = Field(..., alias="instalmentsCapitalPaidInTime")
    instalments_paid_percentage: int | None = Field(None, alias="instalmentsPaidPercentage")
    history: CreditHistory | None = Field(None)

    def export_total_requested(self) -> str:
        """Formats the total requested amount"""
        return format_currency(self.total_requested, currency="CLP", locale="es_CL")

    def export_founding_requests_proportion(self) -> str:
        """Formats the proportion of funding requests paid"""
        return f"{self.funding_requests_paid_count}/{self.funding_requests_count}"
