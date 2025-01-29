from datetime import datetime
from decimal import Decimal
from typing import Any, ClassVar

from cumplo_common.models import PortfolioCategory
from cumplo_common.utils.text import clean_text
from pydantic import BaseModel, Field, field_validator

from .portfolio import Portfolio


class DebtorPortfolio(Portfolio):
    PORTFOLIO_STATUS_MAPPING: ClassVar[dict] = {
        # ON TIME
        "cantidad_pagadas_plazo_normal_pagador": {"status": PortfolioCategory.ON_TIME, "type": "count"},
        "monto_pagadas_plazo_normal_pagador": {"status": PortfolioCategory.ON_TIME, "type": "amount"},
        # CURED
        "cantidad_pagadas_en_mora_pagador": {"status": PortfolioCategory.CURED, "type": "count"},
        "monto_pagadas_en_mora_pagador": {"status": PortfolioCategory.CURED, "type": "amount"},
        # ACTIVE
        "cantidad_operaciones_activas_pagador": {"status": PortfolioCategory.ACTIVE, "type": "count"},
        "monto_operaciones_activas_pagador": {"status": PortfolioCategory.ACTIVE, "type": "amount"},
        # OVERDUE
        "cantidad_operaciones_mora_menor_30_pagador": {"status": PortfolioCategory.OVERDUE, "type": "count"},
        "monto_operaciones_mora_menor_30_pagador": {"status": PortfolioCategory.OVERDUE, "type": "amount"},
        # DELINQUENT
        "cantidad_operaciones_mora_mayor_30_pagador": {"status": PortfolioCategory.DELINQUENT, "type": "count"},
        "monto_operaciones_mora_mayor_30_pagador": {"status": PortfolioCategory.DELINQUENT, "type": "amount"},
        # PAID
        "cantidad_pagadas_pagador": {"status": PortfolioCategory.PAID, "type": "count"},
        "monto_pagadas_pagador": {"status": PortfolioCategory.PAID, "type": "amount"},
        # TOTAL
        "cantidad_total_pagador": {"status": PortfolioCategory.TOTAL, "type": "count"},
        "monto_total_pagador": {"status": PortfolioCategory.TOTAL, "type": "amount"},
        # OUTSTANDING
        "cantidad_vigentes_pagador": {"status": PortfolioCategory.OUTSTANDING, "type": "count"},
        "monto_vigentes_pagador": {"status": PortfolioCategory.OUTSTANDING, "type": "amount"},
    }


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
