from datetime import datetime
from decimal import Decimal
from typing import Any

from cumplo_common.utils.text import clean_text
from pydantic import BaseModel, Field, field_validator, model_validator


class DebtPortfolio(BaseModel):
    active: int = Field(..., alias="cantidad_operaciones_activas_pagador")
    delinquent: int = Field(..., alias="cantidad_operaciones_mora_mayor_30_pagador")
    completed: int = Field(..., alias="cantidad_pagadas_pagador")
    in_time: int = Field(..., alias="cantidad_pagadas_plazo_normal_pagador")
    total_requests: int = Field(..., alias="cantidad_total_pagador")

    @model_validator(mode="before")
    @classmethod
    def round_values(cls, values: dict) -> dict:
        """Round the amount and interest values."""
        for key in [
            "cantidad_operaciones_activas_pagador",
            "cantidad_operaciones_mora_mayor_30_pagador",
            "cantidad_pagadas_pagador",
            "cantidad_total_pagador",
        ]:
            values[key] = round(values[key])
        return values


class Debtor(BaseModel):
    share: Decimal = Field(..., alias="participacion")
    name: str | None = Field(None, alias="nombre_pagador")
    sector: str | None = Field(None, alias="giro_detalle")
    portfolio: DebtPortfolio = Field(..., alias="historial")
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

    @field_validator("sector", mode="before")
    @classmethod
    def _format_sector(cls, value: Any) -> str | None:
        """Clean the value and checks if the IRS sector is 'null' and return None."""
        clean_value = clean_text(value)
        return None if clean_value == "NULL" else clean_value

    @field_validator("portfolio", mode="before")
    @classmethod
    def _format_portfolio(cls, value: Any) -> dict[str, Decimal]:
        """Reformat the portfolio values."""

        def _format_percentage(value: str | int | None) -> Decimal:
            value = str(value) if value else "0"
            return round(Decimal(value.rstrip("%")) / 100, 3) if "%" in value else Decimal(value)

        return {element["tipo"]: _format_percentage(element.get("cantidad")) for element in value}
