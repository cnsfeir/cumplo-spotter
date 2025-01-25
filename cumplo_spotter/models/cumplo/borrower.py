# mypy: disable-error-code="call-overload"

from datetime import datetime
from decimal import Decimal
from typing import Any

from cumplo_common.models import PortfolioStatus
from cumplo_common.utils.text import clean_text
from pydantic import BaseModel, Field, field_validator, model_validator

BORROWER_PORTFOLIO_STATUS_MAPPING = {
    # ON TIME
    "cantidad_pagadas_plazo_normal_solicitante": {"status": PortfolioStatus.ON_TIME, "type": "count"},
    "monto_pagadas_plazo_normal_solicitante": {"status": PortfolioStatus.ON_TIME, "type": "amount"},
    "porcentaje_pagado_plazo_normal": {"status": PortfolioStatus.ON_TIME, "type": "percentage"},
    # CURED
    "cantidad_pagadas_en_mora_solicitante": {"status": PortfolioStatus.CURED, "type": "count"},
    "monto_pagadas_en_mora_solicitante": {"status": PortfolioStatus.CURED, "type": "amount"},
    "porcentaje_pagado_mora": {"status": PortfolioStatus.CURED, "type": "percentage"},
    # ACTIVE
    "cantidad_operaciones_activas_solicitante": {"status": PortfolioStatus.ACTIVE, "type": "count"},
    "monto_operaciones_activas_solicitante": {"status": PortfolioStatus.ACTIVE, "type": "amount"},
    "porcentaje_monto_activo": {"status": PortfolioStatus.ACTIVE, "type": "percentage"},
    # OVERDUE
    "cantidad_operaciones_mora_menor_30_solicitante": {"status": PortfolioStatus.OVERDUE, "type": "count"},
    "monto_operaciones_mora_menor_30_solicitante": {"status": PortfolioStatus.OVERDUE, "type": "amount"},
    "porcentaje_en_mora_menor_30": {"status": PortfolioStatus.OVERDUE, "type": "percentage"},
    # DELINQUENT
    "cantidad_operaciones_mora_mayor_30_solicitante": {"status": PortfolioStatus.DELINQUENT, "type": "count"},
    "monto_operaciones_mora_mayor_30_solicitante": {"status": PortfolioStatus.DELINQUENT, "type": "amount"},
    "porcentaje_en_mora_mayor_30": {"status": PortfolioStatus.DELINQUENT, "type": "percentage"},
    # PAID
    "cantidad_pagadas_solicitante": {"status": PortfolioStatus.PAID, "type": "count"},
    "monto_pagadas_solicitante": {"status": PortfolioStatus.PAID, "type": "amount"},
    # TOTAL
    "cantidad_total_solicitante": {"status": PortfolioStatus.TOTAL, "type": "count"},
    "monto_total_solicitante": {"status": PortfolioStatus.TOTAL, "type": "amount"},
    # OUTSTANDING
    "cantidad_vigentes_solicitante": {"status": PortfolioStatus.OUTSTANDING, "type": "count"},
    "monto_vigentes_solicitante": {"status": PortfolioStatus.OUTSTANDING, "type": "amount"},
}


class BorrowerPortfolioUnit(BaseModel):
    percentage: Decimal = Field(...)
    amount: Decimal = Field(...)
    count: int = Field(...)

    @field_validator("percentage", mode="before")
    @classmethod
    def _format_percentage(cls, value: Any) -> Decimal:
        """Reformat the percentage value."""
        value = str(value) if value else "0"
        return round(Decimal(value.rstrip("%")) / 100, 3)


class BorrowerPortfolio(BaseModel):
    cured: BorrowerPortfolioUnit = Field(...)
    active: BorrowerPortfolioUnit = Field(...)
    overdue: BorrowerPortfolioUnit = Field(...)
    on_time: BorrowerPortfolioUnit = Field(...)
    delinquent: BorrowerPortfolioUnit = Field(...)

    @model_validator(mode="before")
    @classmethod
    def _format_portfolio_data(cls, value: list[dict]) -> dict:
        """Transform portfolio data from list of dicts to structured format."""
        if not isinstance(value, list):
            return value

        portfolio = {
            "cured": {"percentage": 0, "amount": 0, "count": 0},
            "active": {"percentage": 0, "amount": 0, "count": 0},
            "overdue": {"percentage": 0, "amount": 0, "count": 0},
            "on_time": {"percentage": 0, "amount": 0, "count": 0},
            "delinquent": {"percentage": 0, "amount": 0, "count": 0},
        }

        for item in value:
            if not (mapping := BORROWER_PORTFOLIO_STATUS_MAPPING.get(item["tipo"])):
                continue

            if (status := mapping.get("status")) not in portfolio:
                continue

            if (value_type := mapping.get("type")) not in portfolio[status]:
                continue

            portfolio[status][value_type] = item.get("cantidad", 0)

        return portfolio


class Borrower(BaseModel):
    id: int | None = Field(None)
    name: str | None = Field(None, alias="nombre_solicitante")
    average_days_delinquent: int | None = Field(None)
    economic_sector: str | None = Field(None, alias="giro_detalle")
    description: str | None = Field(..., alias="descripcion")
    portfolio: BorrowerPortfolio = Field(..., alias="historial")
    first_appearance: datetime | None = Field(None, alias="fecha_primera_operacion")
    dicom: bool | None = Field(None)

    @field_validator("description", "name", mode="before")
    @classmethod
    def _format_text_field(cls, value: Any) -> str | None:
        """Clean the text value and return None if empty."""
        return clean_text(value) or None

    @field_validator("economic_sector", mode="before")
    @classmethod
    def _format_economic_sector(cls, value: Any) -> str | None:
        """Clean the value and checks if the economic sector is 'null' and return None."""
        clean_value = clean_text(value)
        return None if clean_value == "NULL" else clean_value
