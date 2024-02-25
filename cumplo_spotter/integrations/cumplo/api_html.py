import re
from http import HTTPMethod
from logging import getLogger

import requests
from bs4 import BeautifulSoup
from cumplo_common.utils.text import clean_text

from cumplo_spotter.integrations.cumplo.exceptions import NoResultFound
from cumplo_spotter.utils.constants import AVERAGE_DAYS_DELINQUENT_SELECTOR, CREDIT_DETAIL_TITLE, CUMPLO_HTML_API

logger = getLogger(__name__)


class CumploHTMLAPI:
    """
    Class to interact with Cumplo's HTML API
    """

    url = CUMPLO_HTML_API

    @classmethod
    def _request(cls, method: HTTPMethod, endpoint: str, payload: dict | None = None) -> requests.Response:
        """
        Makes a request to Cumplo's HTML API

        Args:
            method (HTTPMethod): HTTP method to use
            endpoint (str): Endpoint to call
            payload (dict): Payload to send

        Returns:
            requests.Response: Response from the API
        """
        return requests.request(method=method, url=f"{cls.url}{endpoint}", json=payload)

    @classmethod
    def get_funding_requests(cls, id_funding_request: int) -> BeautifulSoup:
        """
        Queries the Cumplo's HTML API for the given funding request information

        Args:
            id_funding_request (int): The ID of the funding request

        Raises:
            NoResultFound: If the funding request information is not available

        Returns:
            BeautifulSoup: The parsed HTML of the funding request
        """
        logger.debug(f"Getting funding request {id_funding_request} from Cumplo's HTML API")
        response = cls._request(HTTPMethod.GET, f"/{id_funding_request}")
        soup = BeautifulSoup(response.text, "html.parser")

        if CREDIT_DETAIL_TITLE not in clean_text(soup.get_text()):
            logger.warning(f"Couldn't get funding request {id_funding_request} from Cumplo's HTML API")
            raise NoResultFound()

        return soup

    @classmethod
    def get_average_days_delinquent(cls, id_funding_request: int) -> int | None:
        """
        Obtains the average days delinquent from a given funding request

        Args:
            id_funding_request (int): The ID of the funding request

        Returns:
            int | None: The average days delinquent or None if the information is not available
        """
        try:
            soup = cls.get_funding_requests(id_funding_request)
        except NoResultFound:
            return None

        element = soup.select_one(AVERAGE_DAYS_DELINQUENT_SELECTOR)
        value = re.findall(r"\d+", element.get_text())
        return int(value[0]) if value else 0
