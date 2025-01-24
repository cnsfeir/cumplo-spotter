from decimal import Decimal
from functools import cached_property
from http import HTTPMethod
from logging import getLogger
from typing import Any

import requests
from cumplo_common.models.currency import Currency
from pydantic import BaseModel, Field, field_validator
from retry import retry

from cumplo_spotter.models.cumplo.funding_request import CumploCreditType
from cumplo_spotter.models.cumplo.request_duration import CumploFundingRequestDuration
from cumplo_spotter.utils.constants import CUMPLO_GLOBAL_API, SIMULATION_AMOUNT

logger = getLogger(__name__)


class GlobalFundingRequest(BaseModel):
    id: int = Field(...)
    score: Decimal = Field(...)
    irr: Decimal = Field(..., alias="tir")
    currency: Currency = Field(..., alias="moneda")
    duration: CumploFundingRequestDuration = Field(..., alias="plazo")
    raised_percentage: Decimal = Field(..., alias="porcentaje_inversion")
    credit_type: CumploCreditType = Field(...)
    id_borrower: int | None = Field(None)

    @field_validator("raised_percentage", mode="before")
    @classmethod
    def raised_percentage_validator(cls, value: Any) -> Decimal:
        """Validate that the raised percentage is a valid decimal number."""
        return round(Decimal(int(value) / 100), 2)

    @cached_property
    def is_completed(self) -> bool:
        """Check if the funding request is fully funded."""
        return self.raised_percentage == Decimal(1)


class CumploGlobalAPI:
    """Class to interact with Cumplo's Global API."""

    url = CUMPLO_GLOBAL_API

    @classmethod
    def _request(cls, method: HTTPMethod, endpoint: str, payload: dict | None = None) -> requests.Response:
        """
        Make a request to Cumplo's Global API.

        Args:
            method (HTTPMethod): HTTP method to use
            endpoint (str): Endpoint to call
            payload (dict): Payload to send

        Returns:
            requests.Response: Response from the API

        """
        return requests.request(method=method, url=f"{cls.url}{endpoint}", json=payload)

    @classmethod
    @retry(requests.exceptions.JSONDecodeError, tries=5, delay=1)
    def get_funding_request(cls, id_funding_request: int) -> dict:
        """
        Query the Cumplo's Global API for the given funding request information.

        Args:
            id_funding_request (int): The ID of the funding request

        Returns:
            dict: The funding request information

        """
        logger.debug(f"Getting funding request {id_funding_request} from Cumplo's Global API")
        response = cls._request(HTTPMethod.GET, f"/inversionista/operacion/{id_funding_request}/CL/historial")
        return response.json()["data"]["attributes"]

    @classmethod
    @retry(requests.exceptions.JSONDecodeError, tries=5, delay=1)
    def simulate_funding_request(cls, funding_request: GlobalFundingRequest, due_date: str) -> dict:
        """
        Request the Cumplo's Global API to simulate the funding request.

        Args:
            funding_request (GlobalFundingRequest): The funding request information
            due_date (str): The due date of the funding request
        Returns:
            dict: The funding request information

        """
        logger.debug(f"Simulating funding request {funding_request.id} from Cumplo's Global API")
        # NOTE: The payload is hardcoded because the simulation only depends on the funding request ID and the amount
        payload = {
            "data": {
                "cuotas": 1,
                "id_operacion": funding_request.id,
                "monto_simulacion": SIMULATION_AMOUNT,
                "plazo": funding_request.duration.value,
                "tasa_anual": float(funding_request.irr),
                "fecha_vencimiento": due_date,
            },
        }
        endpoint = f"//simulador/inversionista/{funding_request.credit_type.value}/CL/CLP"
        response = cls._request(HTTPMethod.POST, endpoint, payload=payload)
        return response.json()["data"]["attributes"]

    @classmethod
    @retry((KeyError, requests.exceptions.JSONDecodeError), tries=5, delay=1)
    def get_funding_requests(cls, *, ignore_completed: bool = False) -> list[GlobalFundingRequest]:
        """
        Query the Cumplo's Global API for the existing funding requests.

        Returns:
            list[FundingRequest]: List of the existing funding requests

        """
        logger.debug("Getting funding requests from Cumplo's Global API")
        response = cls._request(HTTPMethod.GET, "/operaciones/vitrina/sin-historial/CL")

        data = [x["attributes"] for x in response.json()["data"]]

        funding_requests = [
            GlobalFundingRequest.model_validate({
                **element["operacion"],
                "credit_type": element["operacion"]["producto"]["codigo"],
                "id_borrower": element["empresa"]["id"],
            })
            for element in data
        ]

        if ignore_completed:
            funding_requests = [x for x in funding_requests if not x.is_completed]

        return funding_requests
