# mypy: disable-error-code="call-overload"
# pylint: disable=no-member

from enum import Enum

from cumplo_common.models.pydantic import ValidatorMode
from pydantic import BaseModel, Field, field_validator


class DurationUnit(str, Enum):
    MONTH = "MONTH"
    DAY = "DAY"


class FundingRequestDuration(BaseModel):
    unit: DurationUnit = Field(..., alias="type")
    value: int = Field(...)

    def __str__(self) -> str:
        return f"{self.value} {self.unit}"

    @field_validator("unit", mode=ValidatorMode.BEFORE)
    @classmethod
    def unit_formatter(cls, value: str) -> DurationUnit:
        """Formats the unit value"""
        return DurationUnit(value.strip().upper())
