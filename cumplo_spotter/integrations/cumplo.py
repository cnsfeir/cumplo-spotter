import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from decimal import Decimal
from logging import getLogger

import requests
from bs4 import BeautifulSoup
from cumplo_common.models.funding_request import FundingRequest
from cumplo_common.utils.text import clean_text
from lxml.etree import HTML
from retry import retry

from cumplo_spotter.models.funding_request import CumploFundingRequest
from cumplo_spotter.utils.constants import (
    AVERAGE_DAYS_DELINQUENT_SELECTOR,
    CREDIT_DETAIL_TITLE,
    CUMPLO_GRAPHQL_API,
    CUMPLO_REST_API,
    DICOM_STRINGS,
    IRS_SECTOR_SELECTOR,
    PAID_FUNDING_REQUESTS_COUNT_SELECTOR,
    PAID_IN_TIME_PERCENTAGE_SELECTOR,
    SUPPORTING_DOCUMENTS_XPATH,
    TOTAL_AMOUNT_REQUESTED_SELECTOR,
)

logger = getLogger(__name__)


@retry(KeyError, tries=5, delay=1)
def get_available_funding_requests() -> list[FundingRequest]:
    """
    Queries the Cumplo's GraphQL API and returns a list of available funding requests

    Returns:
        list[FundingRequest]: List of available funding requests
    """
    logger.info("Getting funding requests from Cumplo API")
    payload = _build_funding_requests_query()
    response = requests.post(CUMPLO_GRAPHQL_API, json=payload, headers={"Accept-Language": "es-CL"})
    results = response.json()["data"]["fundingRequests"]["results"]

    funding_requests = []
    for result in results:
        funding_request = CumploFundingRequest(**result["operacion"], borrower=result["empresa"])
        if not funding_request.is_completed:
            funding_requests.append(funding_request)

    logger.info(f"Found {len(funding_requests)} available funding requests")
    funding_requests = _gather_funding_requests_details(funding_requests)
    return [request.export() for request in funding_requests]


def _gather_funding_requests_details(funding_requests: list[CumploFundingRequest]) -> list[CumploFundingRequest]:
    """
    Gathers all the details of the received funding requests

    Args:
        funding_requests (list[CumploFundingRequest]): A list of Cumplo funding requests

    Returns:
        list[CumploFundingRequest]: A list of Cumplo funding requests with their details
    """
    with ThreadPoolExecutor(max_workers=20) as executor:
        funding_request_by_future = {
            executor.submit(_get_details, funding_request.id): funding_request for funding_request in funding_requests
        }
        for future in as_completed(funding_request_by_future):
            funding_request = funding_request_by_future[future]

            if soup := future.result():
                _extract_details(funding_request, soup)
            else:
                funding_requests.remove(funding_request)

    logger.info(f"Got {len(funding_requests)} funding requests with credit history")
    return funding_requests


def _get_details(id_funding_request: int) -> BeautifulSoup | None:
    """
    Queries the Cumplo REST API to obtain the credit history from a given funding request's borrower.
    Also, it obtains the supporting documents from the funding request.
    """
    logger.info(f"Getting details from funding request {id_funding_request}")
    response = requests.get(f"{CUMPLO_REST_API}/{id_funding_request}")
    soup = BeautifulSoup(response.text, "html.parser")

    if CREDIT_DETAIL_TITLE not in clean_text(soup.get_text()):
        logger.warning(f"Couldn't get details from funding request {id_funding_request}")
        return None

    return soup


def _extract_details(funding_request: CumploFundingRequest, soup: BeautifulSoup) -> None:
    """
    Extracts the details from a given funding request and updates it

    Args:
        funding_request (FundingRequest): The funding request to update
        soup (BeautifulSoup): The funding request's details page
    """
    funding_request.borrower.dicom = _extract_dicom_status(soup)
    funding_request.borrower.average_days_delinquent = _extract_average_days_delinquent(soup)
    funding_request.borrower.paid_in_time_percentage = _extract_paid_in_time_percentage(soup)
    funding_request.borrower.total_amount_requested = _extract_total_amount_requested(soup)
    funding_request.supporting_documents = _extract_supporting_documents(soup)
    funding_request.borrower.irs_sector = _extract_irs_sector(soup)

    paid_count, requested_count = _extract_funding_requests_count(soup)
    funding_request.borrower.funding_requests_count = requested_count
    funding_request.borrower.paid_funding_requests_count = paid_count


def _extract_dicom_status(soup: BeautifulSoup) -> bool:
    """Extracts the DICOM status from a given funding request"""
    return any(string in clean_text(soup.get_text()) for string in DICOM_STRINGS)


def _extract_supporting_documents(soup: BeautifulSoup) -> list[str]:
    """Extracts the supporting documents from a given funding request"""
    supporting_documents = HTML(str(soup)).xpath(SUPPORTING_DOCUMENTS_XPATH)
    return [clean_text(document.text) for document in supporting_documents]


def _extract_irs_sector(soup: BeautifulSoup) -> str:
    """Extracts the supporting documents from a given funding request"""
    element = soup.select_one(IRS_SECTOR_SELECTOR)
    return clean_text(element.get_text())


def _extract_paid_in_time_percentage(soup: BeautifulSoup) -> Decimal:
    """Extracts the paid in time percentage from a given funding request"""
    element = soup.select_one(PAID_IN_TIME_PERCENTAGE_SELECTOR)
    value = re.findall(r"\d+", element.get_text())
    return round(Decimal(int(value[0]) / 100 if value else 0), 2)


def _extract_average_days_delinquent(soup: BeautifulSoup) -> int:
    """Extracts the average days delinquent from a given funding request"""
    element = soup.select_one(AVERAGE_DAYS_DELINQUENT_SELECTOR)
    value = re.findall(r"\d+", element.get_text())
    return int(value[0]) if value else 0


def _extract_funding_requests_count(soup: BeautifulSoup) -> tuple[int, int]:
    """Extracts the paid and requested funding requests count from a given funding request"""
    element = soup.select_one(PAID_FUNDING_REQUESTS_COUNT_SELECTOR)
    paid, requested = re.findall(r"\d+", element.get_text())[:2]
    return int(paid), int(requested)


def _extract_total_amount_requested(soup: BeautifulSoup) -> int:
    """Extracts the paid and requested funding requests count from a given borrower"""
    element = soup.select_one(TOTAL_AMOUNT_REQUESTED_SELECTOR)
    value = re.findall(r"\d+", element.get_text().replace(".", ""))
    return int(value[0]) if value else 0


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
                            historialCumplimiento {cantidad tipo}
                            id
                            logo
                            nombre_fantasia
                        }
                        operacion {
                            id
                            moneda
                            monto_financiar
                            plazo {type value }
                            porcentaje_inversion
                            score
                            tasa_anual
                            tipo_respaldo
                            tir
                        }
                    }
                }
            }
    """,
    }
