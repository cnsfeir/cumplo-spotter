from datetime import datetime
from decimal import Decimal
from typing import Any

from cumplo_common.models import PortfolioStatus
from cumplo_common.utils.text import clean_text
from pydantic import BaseModel, Field, field_validator, model_validator

DEBTOR_PORTFOLIO_STATUS_MAPPING = {
    # ON TIME
    "cantidad_pagadas_plazo_normal_pagador": {"status": PortfolioStatus.ON_TIME, "type": "count"},
    "monto_pagadas_plazo_normal_pagador": {"status": PortfolioStatus.ON_TIME, "type": "amount"},
    # CURED
    "cantidad_pagadas_en_mora_pagador": {"status": PortfolioStatus.CURED, "type": "count"},
    "monto_pagadas_en_mora_pagador": {"status": PortfolioStatus.CURED, "type": "amount"},
    # ACTIVE
    "cantidad_operaciones_activas_pagador": {"status": PortfolioStatus.ACTIVE, "type": "count"},
    "monto_operaciones_activas_pagador": {"status": PortfolioStatus.ACTIVE, "type": "amount"},
    # OVERDUE
    "cantidad_operaciones_mora_menor_30_pagador": {"status": PortfolioStatus.OVERDUE, "type": "count"},
    "monto_operaciones_mora_menor_30_pagador": {"status": PortfolioStatus.OVERDUE, "type": "amount"},
    # DELINQUENT
    "cantidad_operaciones_mora_mayor_30_pagador": {"status": PortfolioStatus.DELINQUENT, "type": "count"},
    "monto_operaciones_mora_mayor_30_pagador": {"status": PortfolioStatus.DELINQUENT, "type": "amount"},
    # PAID
    "cantidad_pagadas_pagador": {"status": PortfolioStatus.PAID, "type": "count"},
    "monto_pagadas_pagador": {"status": PortfolioStatus.PAID, "type": "amount"},
    # TOTAL
    "cantidad_total_pagador": {"status": PortfolioStatus.TOTAL, "type": "count"},
    "monto_total_pagador": {"status": PortfolioStatus.TOTAL, "type": "amount"},
    # OUTSTANDING
    "cantidad_vigentes_pagador": {"status": PortfolioStatus.OUTSTANDING, "type": "count"},
    "monto_vigentes_pagador": {"status": PortfolioStatus.OUTSTANDING, "type": "amount"},
}


class DebtorPortfolioUnit(BaseModel):
    percentage: Decimal = Field(...)
    amount: Decimal = Field(...)
    count: int = Field(...)


class DebtorPortfolio(BaseModel):
    cured: DebtorPortfolioUnit = Field(...)
    active: DebtorPortfolioUnit = Field(...)
    overdue: DebtorPortfolioUnit = Field(...)
    on_time: DebtorPortfolioUnit = Field(...)
    delinquent: DebtorPortfolioUnit = Field(...)

    @model_validator(mode="before")
    @classmethod
    def _format_portfolio_data(cls, value: list[dict]) -> dict:
        """Transform portfolio data from list of dicts to structured format."""
        if not isinstance(value, list):
            return value

        portfolio: dict[str, dict[str, Decimal | int]] = {
            "cured": {"percentage": Decimal(0), "amount": Decimal(0), "count": 0},
            "active": {"percentage": Decimal(0), "amount": Decimal(0), "count": 0},
            "overdue": {"percentage": Decimal(0), "amount": Decimal(0), "count": 0},
            "on_time": {"percentage": Decimal(0), "amount": Decimal(0), "count": 0},
            "delinquent": {"percentage": Decimal(0), "amount": Decimal(0), "count": 0},
        }

        for item in value:
            if not (mapping := DEBTOR_PORTFOLIO_STATUS_MAPPING.get(item["tipo"])):
                continue

            if (status := mapping.get("status")) not in portfolio:
                continue

            if (value_type := mapping.get("type")) not in portfolio[status]:
                continue

            portfolio[status][value_type] = item.get("cantidad", 0)

        # NOTE: Calculate percentages based since the API only returns the amount and count
        total_count = sum(portfolio[status]["count"] for status in portfolio)
        if total_count > 0:
            for element in portfolio.values():
                element["percentage"] = round(Decimal(element["count"] / total_count), 3)

        return portfolio


class Debtor(BaseModel):
    share: Decimal = Field(..., alias="participacion")
    name: str | None = Field(None, alias="nombre_pagador")
    economic_sector: str | None = Field(None, alias="giro_detalle")
    portfolio: DebtorPortfolio = Field(..., alias="historial")
    description: str | None = Field(..., alias="descripcion")
    first_appearance: datetime = Field(..., alias="fecha_primera_operacion")
    dicom: bool | None = Field(None)

    @field_validator("name", mode="before")
    @classmethod
    def _format_name(cls, value: Any) -> str | None:
        """Clean the value and checks if the name is empty and returns None."""
        return clean_text(value) or None

    @field_validator("description", mode="before")
    @classmethod
    def _format_description(cls, value: Any) -> str | None:
        """Clean the value and checks if the description is empty and return None."""
        return clean_text(value) or None

    @field_validator("economic_sector", mode="before")
    @classmethod
    def _format_economic_sector(cls, value: Any) -> str | None:
        """Clean the value and checks if the economic sector is 'null' and return None."""
        clean_value = clean_text(value)
        return None if clean_value == "NULL" else clean_value
