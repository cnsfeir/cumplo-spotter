# pylint: disable=no-member

from decimal import Decimal
from typing import Any

from pydantic import BaseModel, Field, PositiveInt

from utils.constants import DEFAULT_EXPIRATION_MINUTES, DEFAULT_FILTER_NOTIFIED


class Configuration(BaseModel):
    id: int = Field(...)
    name: str = Field("")
    filter_dicom: bool = Field(False)
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

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        if self.filter_notified is True and self.expiration_minutes is None:
            self.expiration_minutes = DEFAULT_EXPIRATION_MINUTES

    def __hash__(self) -> int:
        exclude = {"id", "name", "expiration_minutes"}
        return hash(self.json(exclude=exclude, exclude_defaults=True, exclude_none=True))

    def __eq__(self, other: Any) -> bool:
        return self.__hash__() == other.__hash__()

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
