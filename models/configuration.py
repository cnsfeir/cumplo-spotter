# pylint: disable=no-member

from decimal import Decimal
from typing import Any

from pydantic import BaseModel, Field

from utils.constants import DEFAULT_FILTER_NOTIFIED, DEFAULT_NOTIFICATION_EXPIRATION


class Configuration(BaseModel):
    id: int = Field(...)
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

    def serialize(self, to_firestore: bool = False) -> dict[str, Any]:
        """Serializes a configuration"""
        if to_firestore:
            content = self.dict(exclude_none=True, exclude={"id"})
            for key, value in content.items():
                if isinstance(value, Decimal):
                    content[key] = float(value)
            return content

        return self.dict(exclude_none=True)

    # TODO: Add filter by credit type
    # TODO: Add filter by minimum investment amount
    # TODO: Add filter by average investment amount
    # TODO: Add filter by average investments per user
