from http import HTTPMethod
from logging import getLogger

import requests
from retry import retry

from cumplo_spotter.utils.constants import CUMPLO_GRAPHQL_API

logger = getLogger(__name__)


class CumploGraphQLAPI:
    """
    Class to interact with Cumplo's GraphQL API
    """

    url = CUMPLO_GRAPHQL_API
    headers = {"Accept-Language": "es-CL"}

    @classmethod
    def _request(cls, method: HTTPMethod, payload: dict | None = None) -> requests.Response:
        """
        Makes a request to Cumplo's GraphQL API

        Args:
            method (HTTPMethod): HTTP method to use
            payload (dict): Payload to send

        Returns:
            requests.Response: Response from the API
        """
        return requests.request(method=method, url=cls.url, json=payload, headers=cls.headers)

    @classmethod
    @retry((KeyError, requests.exceptions.JSONDecodeError), tries=5, delay=1)
    def get_funding_requests(cls, ignore_completed: bool = False) -> list[dict]:
        """
        Queries the Cumplo's GraphQL API for the existing funding requests

        Returns:
            list[dict]: List of the existing funding requests
        """
        logger.debug("Getting funding requests from Cumplo's GraphQL API")
        payload = cls._build_funding_requests_query()
        response = cls._request(HTTPMethod.POST, payload)
        data = response.json()["data"]["fundingRequests"]

        if data["allCompleted"] and ignore_completed:
            logger.info("All funding requests are completed. Ignoring them")
            return []

        # NOTE: This is a compatibility fix to not overwrite a field with the same name from the Global API
        for element in data["results"]:
            element["operacion"]["tipo_credito"] = element["operacion"].pop("tipo_respaldo")

        return data["results"]

    @staticmethod
    def _build_funding_requests_query(limit: int = 50, page: int = 1) -> dict:
        """
        Builds the GraphQL query to fetch funding requests
        """
        return {
            "operationName": "FundingRequests",
            "variables": {"page": page, "limit": limit},
            "query": """
                query FundingRequests($page: Int!, $limit: Int!, $state: Int, $ordering: String) {
                    fundingRequests(page: $page, limit: $limit, state: $state, ordering: $ordering) {
                        count allCompleted results {
                            empresa {
                                id
                            }
                            operacion {
                                id
                                score
                                tipo_respaldo
                            }
                        }
                    }
                }
        """,
        }
