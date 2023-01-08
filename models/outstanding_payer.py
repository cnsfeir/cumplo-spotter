from pydantic import BaseModel, Field


class OutstandingPayer(BaseModel):
    id: str | None = Field(None)
    image: str | None = Field(None)
    business_name: str | None = Field(None, alias="businessName")
