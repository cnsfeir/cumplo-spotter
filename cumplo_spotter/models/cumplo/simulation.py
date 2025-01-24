from datetime import datetime

from cumplo_common.utils.text import clean_text
from pydantic import BaseModel, Field, model_validator

from cumplo_spotter.utils.constants import CUMPLO_POINTS_KEY, PLATFORM_FEE_KEY


class CumploSimulationInstallment(BaseModel):
    interest: int = Field(..., alias="interes")
    amount: int = Field(..., alias="monto_cuota")
    due_date: datetime = Field(..., alias="fecha_vencimiento")

    @model_validator(mode="before")
    @classmethod
    def round_values(cls, values: dict) -> dict:
        """Round the amount and interest values."""
        values["monto_cuota"] = round(values["monto_cuota"])
        values["interes"] = round(values["interes"])
        return values


class CumploFundingRequestSimulation(BaseModel):
    cumplo_points: int = Field(...)
    platform_fee: int = Field(...)
    net_returns: int = Field(...)
    payment_schedule: list[CumploSimulationInstallment] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def round_values(cls, values: dict) -> dict:
        """Round the amount and interest values."""
        values["cumplo_points"] = round(values["cumplo_points"])
        values["platform_fee"] = round(values["platform_fee"])
        values["net_returns"] = round(values["net_returns"])
        return values

    @model_validator(mode="before")
    @classmethod
    def format_values(cls, values: dict) -> dict:
        """Format the values to the expected format."""
        return cls._unpack_simulation(values)

    @staticmethod
    def _unpack_simulation(values: dict) -> dict:
        """Unpack the simulation values."""
        result = {
            "net_returns": values["ganancia_liquida"],
            "payment_schedule": values["forma_pago"],
        }
        for cost in values["costos"]["valores"]:
            if CUMPLO_POINTS_KEY in clean_text(cost["nombre"]):
                result["cumplo_points"] = cost["valor"]
            elif PLATFORM_FEE_KEY in clean_text(cost["nombre"]):
                result["platform_fee"] = cost["valor"]

        return result
