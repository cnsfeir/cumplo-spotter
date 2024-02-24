from http import HTTPMethod
from logging import getLogger

import arrow
import requests
from retry import retry

from cumplo_spotter.utils.constants import CUMPLO_GLOBAL_API, SIMULATION_AMOUNT

logger = getLogger(__name__)


class CumploGlobalAPI:
    """
    Class to interact with Cumplo's Global API
    """

    url = CUMPLO_GLOBAL_API

    @classmethod
    def _request(cls, method: HTTPMethod, endpoint: str, payload: dict | None = None) -> requests.Response:
        """
        Makes a request to Cumplo's Global API

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
        Queries the Cumplo's Global API for the given funding request information

        Args:
            id_funding_request (int): The ID of the funding request

        Returns:
            dict: The funding request information
        """
        logger.debug(f"Getting funding request {id_funding_request} from Cumplo's Global API")
        response = cls._request(HTTPMethod.GET, f"/inversionista/operacion/{id_funding_request}/CL")
        return response.json()["data"]["attributes"]

    @classmethod
    @retry(requests.exceptions.JSONDecodeError, tries=5, delay=1)
    def simulate_funding_request(cls, id_funding_request: int) -> dict:
        """
        Requests the Cumplo's Global API to simulate the funding request

        Args:
            id_funding_request (int): The ID of the funding request

        Returns:
            dict: The funding request information
        """
        logger.debug(f"Simulating funding request {id_funding_request} from Cumplo's Global API")
        # NOTE: The payload is hardcoded because the simulation only depends on the funding request ID and the amount
        payload = {
            "data": {
                "fecha_vencimiento": arrow.utcnow().isoformat(),
                "monto_simulacion": SIMULATION_AMOUNT,
                "id_operacion": id_funding_request,
                "tasa_anual": 10,
                "cuotas": 1,
                "plazo": 1,
            }
        }
        response = cls._request(HTTPMethod.POST, "/simulador/inversionista/ANTICIPO_FACTURA/CL/CL", payload=payload)
        return response.json()["data"]["attributes"]
