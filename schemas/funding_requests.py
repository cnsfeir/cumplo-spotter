from pydantic import BaseModel, Field

from models.funding_request import FundingRequest


class FilterFundingRequestPayload(BaseModel):
    id_user: str = Field("")
    funding_requests: list[FundingRequest] = Field(default_factory=list)
