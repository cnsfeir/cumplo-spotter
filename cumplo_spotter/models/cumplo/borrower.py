# mypy: disable-error-code="call-overload"

from decimal import Decimal

from cumplo_common.models.pydantic import ValidatorMode
from pydantic import BaseModel, Field, model_validator


class CumploBorrower(BaseModel):
    id: int | None = Field(None)
    dicom: bool | None = Field(None)
    irs_sector: str | None = Field(None)
    total_amount_requested: int = Field(0)
    paid_funding_requests_count: int = Field(0)
    average_days_delinquent: int | None = Field(None)
    name: str | None = Field(None, alias="nombre_fantasia")
    funding_requests_count: int = Field(0, alias="activas")
    paid_in_time_percentage: Decimal = Field(alias="pagadas_tiempo")

    @model_validator(mode=ValidatorMode.BEFORE)
    @classmethod
    def format_values(cls, values: dict) -> dict:
        """Formats the values to the expected format"""
        values = cls._unpack_credit_history(values)
        return values

    @staticmethod
    def _unpack_credit_history(values: dict) -> dict:
        """Unpacks the credit history"""
        credit_history = values.pop("historialCumplimiento", [])
        values.update({element["tipo"]: element["cantidad"] for element in credit_history})
        return values
