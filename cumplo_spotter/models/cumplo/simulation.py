from datetime import datetime

from cumplo_common.utils.text import clean_text
from pydantic import BaseModel, Field, model_validator

from cumplo_spotter.utils.constants import CUMPLO_POINTS_KEY, PLATFORM_FEE_KEY


class CumploSimulationInstallment(BaseModel):
    interest: int = Field(..., alias="interes")
    amount: int = Field(..., alias="monto_cuota")
    due_date: datetime = Field(..., alias="fecha_vencimiento")


class CumploFundingRequestSimulation(BaseModel):
    cumplo_points: int = Field(...)
    platform_fee: int = Field(...)
    net_returns: int = Field(...)
    payment_schedule: list[CumploSimulationInstallment] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def format_values(cls, values: dict) -> dict:
        """Formats the values to the expected format"""
        values = cls._unpack_simulation(values)
        return values

    @staticmethod
    def _unpack_simulation(values: dict) -> dict:
        """
        Unpacks the simulation values
        """
        simulation = values.get("data", {}).get("attributes")
        result = {
            "net_returns": simulation["ganancia_liquida"],
            "payment_schedule": simulation["forma_pago"],
        }
        for cost in simulation["costos"]["valores"]:
            if CUMPLO_POINTS_KEY in clean_text(cost["nombre"]):
                result["cumplo_points"] = cost["valor"]
            elif PLATFORM_FEE_KEY in clean_text(cost["nombre"]):
                result["platform_fee"] = cost["valor"]

        return result
