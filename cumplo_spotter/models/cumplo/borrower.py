# mypy: disable-error-code="call-overload"

from datetime import datetime
from typing import Any, ClassVar

from cumplo_common.models import PortfolioCategory
from cumplo_common.utils.text import clean_text
from pydantic import BaseModel, Field, field_validator

from .portfolio import Portfolio


class BorrowerPortfolio(Portfolio):
    PORTFOLIO_STATUS_MAPPING: ClassVar[dict] = {
        # ON TIME
        "cantidad_pagadas_plazo_normal_solicitante": {"status": PortfolioCategory.ON_TIME, "type": "count"},
        "monto_pagadas_plazo_normal_solicitante": {"status": PortfolioCategory.ON_TIME, "type": "amount"},
        "porcentaje_pagado_plazo_normal": {"status": PortfolioCategory.ON_TIME, "type": "percentage"},
        # CURED
        "cantidad_pagadas_en_mora_solicitante": {"status": PortfolioCategory.CURED, "type": "count"},
        "monto_pagadas_en_mora_solicitante": {"status": PortfolioCategory.CURED, "type": "amount"},
        "porcentaje_pagado_mora": {"status": PortfolioCategory.CURED, "type": "percentage"},
        # ACTIVE
        "cantidad_operaciones_activas_solicitante": {"status": PortfolioCategory.ACTIVE, "type": "count"},
        "monto_operaciones_activas_solicitante": {"status": PortfolioCategory.ACTIVE, "type": "amount"},
        "porcentaje_monto_activo": {"status": PortfolioCategory.ACTIVE, "type": "percentage"},
        # OVERDUE
        "cantidad_operaciones_mora_menor_30_solicitante": {"status": PortfolioCategory.OVERDUE, "type": "count"},
        "monto_operaciones_mora_menor_30_solicitante": {"status": PortfolioCategory.OVERDUE, "type": "amount"},
        "porcentaje_en_mora_menor_30": {"status": PortfolioCategory.OVERDUE, "type": "percentage"},
        # DELINQUENT
        "cantidad_operaciones_mora_mayor_30_solicitante": {"status": PortfolioCategory.DELINQUENT, "type": "count"},
        "monto_operaciones_mora_mayor_30_solicitante": {"status": PortfolioCategory.DELINQUENT, "type": "amount"},
        "porcentaje_en_mora_mayor_30": {"status": PortfolioCategory.DELINQUENT, "type": "percentage"},
        # PAID
        "cantidad_pagadas_solicitante": {"status": PortfolioCategory.PAID, "type": "count"},
        "monto_pagadas_solicitante": {"status": PortfolioCategory.PAID, "type": "amount"},
        # TOTAL
        "cantidad_total_solicitante": {"status": PortfolioCategory.TOTAL, "type": "count"},
        "monto_total_solicitante": {"status": PortfolioCategory.TOTAL, "type": "amount"},
        # OUTSTANDING
        "cantidad_vigentes_solicitante": {"status": PortfolioCategory.OUTSTANDING, "type": "count"},
        "monto_vigentes_solicitante": {"status": PortfolioCategory.OUTSTANDING, "type": "amount"},
    }


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
