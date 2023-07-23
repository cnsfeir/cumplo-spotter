import re
from asyncio import ensure_future, gather
from copy import copy
from decimal import Decimal
from logging import getLogger

import requests
from aiohttp import ClientSession
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from lxml.etree import HTML
from retry import retry

from models.configuration import Configuration
from models.filter import (
    AmountRequestedFilter,
    AverageDaysDelinquentFilter,
    CreditsRequestedFilter,
    DicomFilter,
    DurationFilter,
    IRRFilter,
    MonthlyProfitFilter,
    NotificationFilter,
    PaidInTimeFilter,
    ScoreFilter,
)
from models.funding_request import FundingRequest, FundingRequestExtraInformation
from models.user import User
from utils.constants import (
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
from utils.text import clean_text

load_dotenv()
logger = getLogger(__name__)


def filter_funding_requests(
    funding_requests: list[FundingRequest], user: User, configuration: Configuration
) -> list[FundingRequest]:
    """
    Gets all the GOOD available funding requests from the Cumplo API.
    """
    filters = [
        ScoreFilter(configuration),
        IRRFilter(configuration),
        MonthlyProfitFilter(configuration),
        DurationFilter(configuration),
        DicomFilter(configuration),
        PaidInTimeFilter(configuration),
        AmountRequestedFilter(configuration),
        CreditsRequestedFilter(configuration),
        AverageDaysDelinquentFilter(configuration),
        NotificationFilter(configuration, user),
    ]

    logger.info(f"Applying {len(filters)} filters to {len(funding_requests)} funding requests")
    funding_requests = list(filter(lambda x: all(filter_.apply(x) for filter_ in filters), funding_requests))

    logger.info(f"Got {len(funding_requests)} funding requests after applying filters")
    return funding_requests


@retry(KeyError, tries=5, delay=1)
async def get_available_funding_requests() -> list[FundingRequest]:
    """
    Queries the Cumplo's GraphQL API and returns a list of available FundingRequest ordered by monthly profit rate
    """
    logger.info("Getting funding requests from Cumplo API")

    payload = _build_all_funding_requests_query()
    response = requests.post(CUMPLO_GRAPHQL_API, json=payload, headers={"Accept-Language": "es-CL"})
    results = response.json()["data"]["fundingRequests"]["results"]

    funding_requests: list[FundingRequest] = []
    for result in results:
        funding_request = FundingRequest(**result["operacion"], borrower=result["empresa"])
        if not funding_request.is_completed:
            funding_requests.append(funding_request)

    logger.info(f"Found {len(funding_requests)} funding requests")
    funding_requests = await _gather_full_funding_requests(funding_requests)

    funding_requests.sort(key=lambda x: x.monthly_profit_rate, reverse=True)
    logger.info(f"Finish sorting {len(funding_requests)} funding requests by monthly profit rate")

    return funding_requests


async def _gather_full_funding_requests(funding_requests: list[FundingRequest]) -> list[FundingRequest]:
    """
    Gathers the full information of the received funding requests.
    """
    tasks = []
    async with ClientSession() as session:
        for funding_request in funding_requests:
            tasks.append(ensure_future(_get_extra_information(session, funding_request.id)))

        logger.info(f"Gathering {len(tasks)} credit history")
        extra_information = await gather(*tasks)
        for funding_request, information in zip(copy(funding_requests), extra_information):
            if information is None:
                funding_requests.remove(funding_request)
                continue

            funding_request.borrower.dicom = information.dicom
            funding_request.borrower.average_days_delinquent = information.average_days_delinquent
            funding_request.borrower.paid_in_time_percentage = information.paid_in_time_percentage
            funding_request.borrower.total_amount_requested = information.total_amount_requested
            funding_request.borrower.funding_requests_count = information.funding_requests_count
            funding_request.borrower.paid_funding_requests_count = information.paid_funding_requests_count
            funding_request.supporting_documents = information.supporting_documents
            funding_request.borrower.irs_sector = information.irs_sector

    logger.info(f"Got {len(funding_requests)} funding requests with credit history")
    return funding_requests


async def _get_extra_information(
    session: ClientSession, id_funding_request: int
) -> FundingRequestExtraInformation | None:
    """
    Queries the Cumplo API and returns the credit history and the supporting documents from a
    given funding request's borrower
    """
    logger.info(f"Getting credit history from funding request {id_funding_request}")
    async with session.get(f"{CUMPLO_REST_API}/{id_funding_request}") as response:
        text = await response.text()
        soup = BeautifulSoup(text, "html.parser")

        if CREDIT_DETAIL_TITLE not in (content := clean_text(soup.get_text())):
            logger.warning(f"Couldn't get extra information from funding request {id_funding_request}")
            return None

        paid, requested = _extract_funding_requests_count(soup)

        return FundingRequestExtraInformation(
            funding_requests_count=requested,
            paid_funding_requests_count=paid,
            irs_sector=_extract_irs_sector(soup),
            supporting_documents=_extract_supporting_documents(soup),
            total_amount_requested=_extract_total_amount_requested(soup),
            paid_in_time_percentage=_extract_paid_in_time_percentage(soup),
            average_days_delinquent=_extract_average_days_delinquent(soup),
            dicom=any(string in content for string in DICOM_STRINGS),
        )


def _extract_supporting_documents(content: BeautifulSoup) -> list[str]:
    """
    Extracts the supporting documents from a given funding request
    """
    logger.debug("Extracting supporting documents from funding request detail")
    supporting_documents = HTML(str(content)).xpath(SUPPORTING_DOCUMENTS_XPATH)
    return [clean_text(document.text) for document in supporting_documents]


def _extract_irs_sector(content: BeautifulSoup) -> str:
    """
    Extracts the supporting documents from a given funding request
    """
    logger.debug("Extracting IRS sector from funding request detail")
    element = content.select_one(IRS_SECTOR_SELECTOR)
    return clean_text(element.get_text())


def _extract_paid_in_time_percentage(content: BeautifulSoup) -> Decimal:
    """
    Extracts the paid in time percentage from a given funding request
    """
    logger.debug("Extracting paid in time percentage from funding request details")
    element = content.select_one(PAID_IN_TIME_PERCENTAGE_SELECTOR)
    value = re.findall(r"\d+", element.get_text())
    return round(Decimal(int(value[0]) / 100 if value else 0), 2)


def _extract_average_days_delinquent(content: BeautifulSoup) -> int:
    """
    Extracts the average days delinquent from a given funding request
    """
    logger.debug("Extracting average days delinquent from funding request details")
    element = content.select_one(AVERAGE_DAYS_DELINQUENT_SELECTOR)
    value = re.findall(r"\d+", element.get_text())
    return int(value[0]) if value else 0


def _extract_funding_requests_count(content: BeautifulSoup) -> tuple[int, int]:
    """
    Extracts the paid and requested funding requests count from a given funding request
    """
    logger.debug("Extracting paid funding requests count from funding request details")
    element = content.select_one(PAID_FUNDING_REQUESTS_COUNT_SELECTOR)
    paid, requested = re.findall(r"\d+", element.get_text())[:2]
    return int(paid), int(requested)


def _extract_total_amount_requested(content: BeautifulSoup) -> int:
    """
    Extracts the paid and requested funding requests count from a given borrower
    """
    logger.debug("Extracting paid and requested funding requests count from borrower details")
    element = content.select_one(TOTAL_AMOUNT_REQUESTED_SELECTOR)
    value = re.findall(r"\d+", element.get_text().replace(".", ""))
    return int(value[0]) if value else 0


def _build_all_funding_requests_query(limit: int = 50, page: int = 1) -> dict:
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
                            historialCumplimiento {
                                cantidad
                                tipo
                            }
                            id
                            logo
                            nombre_fantasia
                        }
                        operacion {
                            id
                            moneda
                            monto_financiar
                            plazo {
                                type
                                value
                            }
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
