from enum import Enum

from pydantic import BaseModel, Field


class DurationUnit(str, Enum):
    MONTH = "month"
    DAY = "day"


class FundingRequestDuration(BaseModel):
    unit: str = Field(..., alias="type")
    value: int = Field(...)

    def __str__(self) -> str:
        return f"{self.value} {self.unit}"
