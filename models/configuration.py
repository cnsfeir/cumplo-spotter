# pylint: disable=no-member

import os
from decimal import Decimal

from pydantic import BaseModel, Field

FILTER_NOTIFIED = bool(os.getenv("FILTER_NOTIFIED"))
NOTIFICATION_EXPIRATION = int(os.getenv("NOTIFICATION_EXPIRATION", "2"))


class Configuration(BaseModel):
    filter_dicom: bool = Field(False)
    irr: Decimal | None = Field(None)
    duration: int | None = Field(None)
    score: Decimal | None = Field(None)
    amount_requested: int | None = Field(None)
    credits_requested: int | None = Field(None)
    filter_notified: bool = Field(FILTER_NOTIFIED)
    average_days_delinquent: int | None = Field(None)
    monthly_profit_rate: Decimal | None = Field(None)
    paid_in_time_percentage: Decimal | None = Field(None)
    notification_expiration: int = Field(NOTIFICATION_EXPIRATION)
