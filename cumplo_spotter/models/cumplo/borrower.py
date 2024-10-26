# mypy: disable-error-code="call-overload"

from datetime import datetime
from decimal import Decimal
from typing import Any

from cumplo_common.utils.text import clean_text
from pydantic import BaseModel, Field, field_validator


class BorrowerPortfolio(BaseModel):
    active: int = Field(..., alias="activas")
    completed: int = Field(..., alias="completadas")
    total_amount: int = Field(..., alias="monto_total")
    total_requests: int = Field(..., alias="total_operaciones")

    # NOTE: The following fields are based on the total requests and should add up to 100%
    in_time: Decimal = Field(..., alias="pagados_plazo_normal")
    cured: Decimal = Field(..., alias="pagados_mora_mayor_30")
    delinquent: Decimal = Field(..., alias="mora_mayor_30")
    outstanding: Decimal = Field(..., alias="vigente")


class Borrower(BaseModel):
    id: int | None = Field(None)
    average_days_delinquent: int | None = Field(None)
    economic_sector: str | None = Field(None, alias="giro_detalle")
    description: str | None = Field(..., alias="descripcion")
    portfolio: BorrowerPortfolio = Field(..., alias="historial")
    first_appearance: datetime = Field(..., alias="fecha_primera_operacion")
    dicom: bool | None = Field(None)

    @field_validator("description", mode="before")
    @classmethod
    def _format_description(cls, value: Any) -> str | None:
        """Clean the value and checks if the description is empty and returns None."""
        return clean_text(value) or None

    @field_validator("economic_sector", mode="before")
    @classmethod
    def _format_economic_sector(cls, value: Any) -> str | None:
        """Clean the value and checks if the economic sector is 'null' and return None."""
        clean_value = clean_text(value)
        return None if clean_value == "NULL" else clean_value

    @field_validator("portfolio", mode="before")
    @classmethod
    def _format_portfolio(cls, value: Any) -> dict[str, Decimal]:
        """Reformat the portfolio values."""

        def _format_percentage(value: str | int) -> Decimal:
            value = str(value)
            return round(Decimal(value.rstrip("%")) / 100, 3) if "%" in value else Decimal(value)

        return {element["tipo"]: _format_percentage(element["cantidad"]) for element in value}
