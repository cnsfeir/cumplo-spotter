from datetime import datetime
from typing import Self

from cumplo_common.utils.text import clean_text
from pydantic import BaseModel, Field, model_validator

from cumplo_spotter.utils.constants import EXIT_FEE_KEY, SIMULATION_AMOUNT, UPFRONT_FEE_KEY


class CumploSimulationInstallment(BaseModel):
    capital: int = Field(..., alias="capital")
    interest: int = Field(..., alias="interes")
    amount: int = Field(..., alias="montoPagar")
    exit_fee: int = Field(..., alias="feeSalida")
    date: datetime = Field(..., alias="fechaPago")

    @model_validator(mode="before")
    @classmethod
    def round_values(cls, values: dict) -> dict:
        """Round the amount and interest values."""
        for key in ["montoPagar", "interes", "capital", "feeSalida"]:
            if key in values:
                values[key] = round(values[key])
        return values

    @model_validator(mode="after")
    def adjust_amount(self) -> Self:
        """Subtract exit fee from amount after model instantiation."""
        self.amount -= self.exit_fee  # NOTE: The exit fee has to be subtracted from the received amount
        return self


class CumploFundingRequestSimulation(BaseModel):
    exit_fee: int = Field(...)
    upfront_fee: int = Field(...)
    net_returns: int = Field(...)
    installments: list[CumploSimulationInstallment] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def format_values(cls, values: dict) -> dict:
        """Format the values to the expected format."""
        return cls._unpack_simulation(values)

    @staticmethod
    def _unpack_simulation(values: dict) -> dict:
        """Unpack the simulation values."""
        result = {"net_returns": round(values["ganancia_liquida"])}

        for cost in values["costos"]["valores"]:
            if UPFRONT_FEE_KEY in clean_text(cost["nombre"]):
                result["upfront_fee"] = round(cost["valor"])
            elif EXIT_FEE_KEY in clean_text(cost["nombre"]):
                result["exit_fee"] = round(cost["valor"])

        if values.get("cuotas"):
            result["installments"] = values["cuotas"]
        else:
            installment = values["forma_pago"][0]
            result["installments"] = [
                {
                    "capital": SIMULATION_AMOUNT,
                    "feeSalida": result["exit_fee"],
                    "interes": installment["interes"],
                    "montoPagar": installment["monto_cuota"],
                    "fechaPago": installment["fecha_vencimiento"],
                }
            ]

        return result
