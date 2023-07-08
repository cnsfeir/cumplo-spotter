# pylint: disable=no-member

from decimal import Decimal
from typing import Any

from pydantic import BaseModel, Field

from utils.constants import DEFAULT_FILTER_NOTIFIED, DEFAULT_NOTIFICATION_EXPIRATION


class Configuration(BaseModel):
    id: int = Field(..., exclude=True)
    name: str = Field("")
    filter_dicom: bool = Field(False)
    irr: Decimal | None = Field(None)
    duration: int | None = Field(None)
    score: Decimal | None = Field(None)
    amount_requested: int | None = Field(None)
    credits_requested: int | None = Field(None)
    filter_notified: bool = Field(DEFAULT_FILTER_NOTIFIED)
    average_days_delinquent: int | None = Field(None)
    monthly_profit_rate: Decimal | None = Field(None)
    paid_in_time_percentage: Decimal | None = Field(None)
    notification_expiration: int = Field(DEFAULT_NOTIFICATION_EXPIRATION)

    def __hash__(self) -> int:
        return hash(self.json(exclude={"id", "name"}, exclude_defaults=True, exclude_none=True))

    def __eq__(self, wea: Any) -> bool:
        return self.__hash__() == wea.__hash__()

    # TODO: Add filter by credit type
    # TODO: Add filter by minimum investment amount
    # TODO: Add filter by average investment amount
    # TODO: Add filter by average investments per user
