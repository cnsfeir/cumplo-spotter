import os
from asyncio import ensure_future, gather, run
from copy import copy
from decimal import Decimal
from logging import getLogger

import requests
from aiohttp import ClientSession
from bs4 import BeautifulSoup
from bs4.element import Tag
from dotenv import load_dotenv
from lxml.etree import HTML
from retry import retry

from models.configuration import Configuration
from models.filter import (
    AmountReceivedFilter,
    AvailableFilter,
    AverageDaysDelinquentFilter,
    CreditsRequestedFilter,
    DicomFilter,
    DurationFilter,
    Filter,
    IRRFilter,
    MonthlyProfitFilter,
    NotificationFilter,
    PaidInTimeFilter,
    ScoreFilter,
)
from models.funding_request import FundingRequest, FundingRequestExtraInformation
from models.user import User
from utils.text import clean_text

load_dotenv()
logger = getLogger(__name__)


CUMPLO_GRAPHQL_API = os.getenv("CUMPLO_GRAPHQL_API", "")
CUMPLO_FUNDING_REQUESTS_API = os.getenv("CUMPLO_FUNDING_REQUESTS_API", "")
CREDIT_DETAIL_TITLE = os.getenv("CREDIT_DETAIL_TITLE", "INFORMACION DEL CREDITO")

DICOM_STRINGS = ["CON DICOM", "CONDICOM", "PRESENTA DICOM"]
HISTORY_SELECTOR = "span.loan-view-optional-visibility + span"
SUPPORTING_DOCUMENTS_XPATH = "//div[@class='loan-view-documents-section']//img/parent::span/following-sibling::span"


def get_funding_requests(user: User, configuration: Configuration) -> list[FundingRequest]:
    """
    Gets all the GOOD available funding requests from the Cumplo API.
    """
    funding_requests = _get_available_funding_requests()

    filters = [
        AvailableFilter(user),
        ScoreFilter(configuration),
        IRRFilter(configuration),
        MonthlyProfitFilter(configuration),
        DurationFilter(configuration),
    ]
    funding_requests = _filter_funding_requests(funding_requests, *filters)
    logger.info(f"Found {len(funding_requests)} available funding requests")

    funding_requests = run(_gather_full_funding_requests(funding_requests))

    filters = [
        DicomFilter(configuration),
        PaidInTimeFilter(configuration),
        AmountReceivedFilter(configuration),
        CreditsRequestedFilter(configuration),
        AverageDaysDelinquentFilter(configuration),
        NotificationFilter(configuration, user),
    ]
    funding_requests = _filter_funding_requests(funding_requests, *filters)

    funding_requests.sort(key=lambda x: x.monthly_profit_rate, reverse=True)
    logger.debug(f"Finish sorting {len(funding_requests)} funding requests by monthly profit rate")

    return funding_requests


async def _gather_full_funding_requests(funding_requests: list[FundingRequest]) -> list[FundingRequest]:
    """
    Gathers the full information of the received funding requests.
    """
    tasks = []
    async with ClientSession() as session:
        for funding_request in funding_requests:
            tasks.append(ensure_future(_get_extra_information(session, funding_request.id)))

        logger.info(f"Gathering {len(tasks)} credit history responses")
        extra_information = await gather(*tasks)
        for funding_request, information in zip(copy(funding_requests), extra_information):
            if information is None:
                funding_requests.remove(funding_request)
                continue

            funding_request.borrower.dicom = information.dicom
            funding_request.supporting_documents = information.supporting_documents
            funding_request.borrower.paid_in_time_percentage = information.paid_in_time_percentage
            funding_request.borrower.average_days_delinquent = information.average_days_delinquent

    logger.info(f"Got {len(funding_requests)} funding requests with credit history")
    return funding_requests


@retry(KeyError, tries=5, delay=1)
def _get_available_funding_requests() -> list[FundingRequest]:
    """
    Queries the Cumplo's GraphQL API and returns a list of available FundingRequest ordered by monthly profit rate
    """
    logger.debug("Getting funding requests from Cumplo API")

    payload = _build_all_funding_requests_query()
    response = requests.post(CUMPLO_GRAPHQL_API, json=payload, headers={"Accept-Language": "es-CL"})
    results = response.json()["data"]["fundingRequests"]["results"]

    funding_requests = [FundingRequest(**result) for result in results]
    logger.info(f"Found {len(funding_requests)} funding requests")

    return funding_requests


async def _get_extra_information(
    session: ClientSession, id_funding_request: int
) -> FundingRequestExtraInformation | None:
    """
    Queries the Cumplo API and returns the credit history and the supporting documents from a
    given funding request's borrower
    """
    logger.info(f"Getting credit history from funding request {id_funding_request}")
    async with session.get(f"{CUMPLO_FUNDING_REQUESTS_API}/{id_funding_request}") as response:
        text = await response.text()
        soup = BeautifulSoup(text, "html.parser")

        if CREDIT_DETAIL_TITLE not in (content := clean_text(soup.get_text())):
            logger.warning(f"Couldn't get extra information from funding request {id_funding_request}")
            return None

        logger.debug(f"Extracting supporting documents from funding request {id_funding_request} response")
        supporting_documents = HTML(str(soup)).xpath(SUPPORTING_DOCUMENTS_XPATH)

        logger.debug(f"Extracting credit history from funding request {id_funding_request} response")
        history = soup.select(HISTORY_SELECTOR)

        return FundingRequestExtraInformation(
            supporting_documents=[clean_text(document.text) for document in supporting_documents],
            paid_in_time_percentage=Decimal(_extract_history_data(history[1])),
            average_days_delinquent=int(_extract_history_data(history[0])),
            dicom=any(string in content for string in DICOM_STRINGS),
        )


def _extract_history_data(element: Tag) -> str:
    """
    Returns the data from a given element from the "credit history" section with the form "title: data"
    """
    return element.get_text().replace("\n", "").replace("%(*)", "").split(":")[-1].strip()


def _filter_funding_requests(funding_requests: list[FundingRequest], *filters: Filter) -> list[FundingRequest]:
    """
    Filters the funding requests that don't meet the minimum requirements
    """
    logger.debug(f"Applying {len(filters)} filters to {len(funding_requests)} funding requests")
    funding_requests = list(filter(lambda x: all(filter_.apply(x) for filter_ in filters), funding_requests))

    logger.info(f"Got {len(funding_requests)} funding requests after applying filters")
    return funding_requests


def _build_all_funding_requests_query(limit: int = 50, page: int = 1) -> dict:
    """
    Builds the GraphQL query to fetch funding requests
    """
    return {
        "operationName": "FundingRequests",
        "variables": {"limit": limit, "page": page},
        "query": """
            query FundingRequests($page: Int!, $limit: Int!, $state: Int, $ordering: String) {
                fundingRequests(page: $page, limit: $limit, state: $state, ordering: $ordering) {
                    count results {
                        id
                        amount
                        creditType
                        dac duration {
                            type
                            value
                        }
                        fundedAmount
                        outstandingPayer {
                            id
                            businessName
                        }
                        requestable {
                            id
                            fantasyName
                            name
                            fundingRequestsCount
                            fundingRequestsPaidCount
                            instalmentsCapital
                            instalmentsCapitalPaidInTime
                            instalmentsPaidPercentage
                        }
                        tir
                    }
                }
            }
        """,
    }
