from pydantic import BaseModel, Field
from typing import Optional


class OutstandingPayer(BaseModel):
    id: Optional[str] = Field(None)
    image: Optional[str] = Field(None)
    business_name: Optional[str] = Field(None, alias="businessName")
