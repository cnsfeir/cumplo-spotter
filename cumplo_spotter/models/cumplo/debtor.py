from datetime import datetime
from decimal import Decimal
from typing import Any

from cumplo_common.utils.text import clean_text
from pydantic import BaseModel, Field, field_validator


class DebtPortfolio(BaseModel):
    active: int = Field(..., alias="activas")
    delinquent: int = Field(..., alias="mora")
    completed: int = Field(..., alias="completadas")
    in_time: int = Field(..., alias="pagadas_tiempo")
    total_requests: int = Field(..., alias="total_operaciones")


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
