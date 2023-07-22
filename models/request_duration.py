# pylint: disable=no-self-argument, no-member

from enum import Enum

from pydantic import BaseModel, Field, validator


class DurationUnit(str, Enum):
    MONTH = "MONTH"
    DAY = "DAY"


class FundingRequestDuration(BaseModel):
    unit: DurationUnit = Field(..., alias="type")
    value: int = Field(...)

    def __str__(self) -> str:
        return f"{self.value} {self.unit}"

    @validator("unit", pre=True)
    def unit_formatter(cls, value: str) -> DurationUnit:
        """Formats the unit value"""
        return DurationUnit(value.strip().upper())
