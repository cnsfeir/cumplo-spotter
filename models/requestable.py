from pydantic import BaseModel, Field


class Requestable(BaseModel):
    id: str = Field(...)
    name: str | None = Field(None)
    fantasy_name: str = Field(..., alias="fantasyName")
    instalments_capital: int = Field(..., alias="instalmentsCapital")
    funding_requests_count: int = Field(..., alias="fundingRequestsCount")
    funding_requests_paid_count: int = Field(..., alias="fundingRequestsPaidCount")
    instalments_capital_paid_in_time: int = Field(..., alias="instalmentsCapitalPaidInTime")
    instalments_paid_percentage: int | None = Field(None, alias="instalmentsPaidPercentage")
