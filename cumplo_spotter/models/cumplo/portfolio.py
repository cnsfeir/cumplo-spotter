from decimal import Decimal
from typing import ClassVar

from pydantic import BaseModel, Field, model_validator


class PortfolioUnit(BaseModel):
    amount: Decimal = Field(...)
    count: int = Field(...)


class Portfolio(BaseModel):
    cured: PortfolioUnit = Field(...)
    active: PortfolioUnit = Field(...)
    overdue: PortfolioUnit = Field(...)
    on_time: PortfolioUnit = Field(...)
    delinquent: PortfolioUnit = Field(...)

    PORTFOLIO_STATUS_MAPPING: ClassVar[dict] = {}

    @model_validator(mode="before")
    @classmethod
    def _format_portfolio_data(cls, value: list[dict]) -> dict:
        """Transform portfolio data from list of dicts to structured format."""
        if not isinstance(value, list):
            return value

        portfolio = {
            "cured": {"amount": Decimal(0), "count": 0},
            "active": {"amount": Decimal(0), "count": 0},
            "overdue": {"amount": Decimal(0), "count": 0},
            "on_time": {"amount": Decimal(0), "count": 0},
            "delinquent": {"amount": Decimal(0), "count": 0},
        }

        for item in value:
            if not (mapping := cls.PORTFOLIO_STATUS_MAPPING.get(item["tipo"])):
                continue

            if (status := mapping.get("status")) not in portfolio:
                continue

            if (value_type := mapping.get("type")) not in portfolio[status]:
                continue

            portfolio[status][value_type] = item.get("cantidad", 0)

        return portfolio
