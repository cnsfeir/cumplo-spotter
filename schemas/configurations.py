from decimal import Decimal

from pydantic import BaseModel, Field, PositiveInt

from utils.constants import DEFAULT_FILTER_NOTIFIED


class ConfigurationPayload(BaseModel):
    name: str = Field("")
    filter_dicom: bool | None = Field(None)
    irr: Decimal | None = Field(None, ge=0)
    duration: PositiveInt | None = Field(None)
    score: Decimal | None = Field(None, ge=0, le=1)
    amount_requested: PositiveInt | None = Field(None)
    credits_requested: PositiveInt | None = Field(None)
    expiration_minutes: PositiveInt | None = Field(None)
    filter_notified: bool = Field(DEFAULT_FILTER_NOTIFIED)
    monthly_profit_rate: Decimal | None = Field(None, ge=0)
    average_days_delinquent: PositiveInt | None = Field(None)
    paid_in_time_percentage: Decimal | None = Field(None, ge=0, le=1)

    # TODO: Add filter by credit type
    # TODO: Add filter by minimum investment amount
    # TODO: Add filter by average investment amount
    # TODO: Add filter by average investments per user
