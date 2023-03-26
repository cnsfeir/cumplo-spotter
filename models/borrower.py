# pylint: disable=no-member

from decimal import Decimal
from logging import getLogger
from typing import Any

from pydantic import BaseModel, Field

from utils.currency import format_currency

logger = getLogger(__name__)


class Borrower(BaseModel):
    id: str = Field(...)
    name: str = Field(..., alias="fantasyName")
    total_amount_requested: int = Field(..., alias="instalmentsCapital")
    funding_requests_count: int = Field(..., alias="fundingRequestsCount")
    paid_funding_requests_count: int = Field(..., alias="fundingRequestsPaidCount")
    amount_paid_in_time: int = Field(..., alias="instalmentsCapitalPaidInTime")
    paid_in_time_percentage: Decimal | None = Field(None)
    average_days_delinquent: int | None = Field(None)
    dicom: bool | None = Field(None)

    @property
    def paid_funding_requests_percentage(self) -> Decimal:
        """Returns the percentage of instalments paid in time"""
        if not self.funding_requests_count:
            return Decimal(0)
        return round(Decimal(self.paid_funding_requests_count / self.funding_requests_count), 3)

    def dict(self, *args: Any, **kwargs: Any) -> dict:
        """Builds a dictionary with the borrower data"""
        return {
            **super().dict(*args, **kwargs),
            "paid_funding_requests_percentage": self.paid_funding_requests_percentage,
            "total_amount_requested": format_currency(self.total_amount_requested),
            "amount_paid_in_time": format_currency(self.amount_paid_in_time),
        }
