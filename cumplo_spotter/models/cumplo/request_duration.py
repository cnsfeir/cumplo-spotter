# mypy: disable-error-code="call-overload"
# pylint: disable=no-member


from cumplo_common.models.funding_request import DurationUnit
from pydantic import BaseModel, Field, field_validator


class CumploFundingRequestDuration(BaseModel):
    unit: DurationUnit = Field(..., alias="type")
    value: int = Field(...)

    def __str__(self) -> str:
        return f"{self.value} {self.unit}"

    @field_validator("unit", mode="before")
    @classmethod
    def unit_formatter(cls, value: str) -> DurationUnit:
        """Format the unit value."""
        return DurationUnit(value.strip().upper())
