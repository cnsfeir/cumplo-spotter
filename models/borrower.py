from decimal import Decimal

from pydantic import BaseModel, Field


class CumploBorrower(BaseModel):
    id: int | None = Field(None)
    dicom: bool | None = Field(None)
    irs_sector: str | None = Field(None)
    funding_requests_count: int = Field(0)
    total_amount_requested: int = Field(0)
    paid_funding_requests_count: int = Field(0)
    average_days_delinquent: int | None = Field(None)
    paid_in_time_percentage: Decimal | None = Field(None)
    name: str | None = Field(None, alias="nombre_fantasia")
