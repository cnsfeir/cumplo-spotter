# pylint: disable=no-member

from decimal import Decimal
from logging import getLogger
from typing import Any

from cumplo_common.utils.currency import format_currency
from pydantic import BaseModel, Field

logger = getLogger(__name__)


class Borrower(BaseModel):
    id: str | None = Field(None)
    dicom: bool | None = Field(None)
    irs_sector: str | None = Field(None)
    funding_requests_count: int = Field(0)
    total_amount_requested: int = Field(0)
    paid_funding_requests_count: int = Field(0)
    average_days_delinquent: int | None = Field(None)
    paid_in_time_percentage: Decimal | None = Field(None)
    name: str | None = Field(None, alias="nombre_fantasia")

    @property
    def paid_funding_requests_percentage(self) -> Decimal:
        """Returns the percentage of instalments paid in time"""
        if not self.funding_requests_count:
            return Decimal(0)
        return round(Decimal(self.paid_funding_requests_count / self.funding_requests_count), 2)

    @property
    def amount_paid_in_time(self) -> int:
        """Returns the amount paid in time"""
        return round(self.total_amount_requested * self.paid_funding_requests_percentage)

    def dict(self, *args: Any, **kwargs: Any) -> dict:
        """Builds a dictionary with the borrower data"""
        return {
            **super().dict(*args, **kwargs),
            "paid_funding_requests_percentage": self.paid_funding_requests_percentage,
            "total_amount_requested": format_currency(self.total_amount_requested),
            "amount_paid_in_time": format_currency(self.amount_paid_in_time),
        }
