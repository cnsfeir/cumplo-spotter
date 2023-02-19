import os
from asyncio import ensure_future, gather, run
from logging import getLogger

import requests
from aiohttp import ClientSession
from bs4 import BeautifulSoup
from bs4.element import Tag
from dotenv import load_dotenv
from retry import retry

from integrations.firestore import firestore_client
from models.borrower import CreditHistory
from models.configuration import Configuration
from models.filter import (
    AvailableFilter,
    DicomFilter,
    DurationUnitFilter,
    Filter,
    MonthlyProfitFilter,
    NotificationFilter,
    ScoreFilter,
)
from models.funding_request import FundingRequest
from models.request_duration import DurationUnit
from utils.text import clean_text

load_dotenv()
logger = getLogger(__name__)


MIN_SCORE = float(os.getenv("MIN_SCORE", "3.5"))
DICOM_STRING = os.getenv("DICOM_STRING", "CON DICOM")
CUMPLO_GRAPHQL_API = os.getenv("CUMPLO_GRAPHQL_API", "")
MIN_MONTHLY_PROFIT = float(os.getenv("MIN_MONTHLY_PROFIT", "1.5"))
CUMPLO_FUNDING_REQUESTS_API = os.getenv("CUMPLO_FUNDING_REQUESTS_API", "")
CREDIT_DETAIL_TITLE = os.getenv("CREDIT_DETAIL_TITLE", "INFORMACION DEL CREDITO")


def get_funding_requests(configuration: Configuration) -> list[FundingRequest]:
    """
    Gets all the GOOD available funding requests from the Cumplo API.
    """
    funding_requests = get_available_funding_requests()
    notifications = firestore_client.get_notifications()

    filters = [
        AvailableFilter(notifications),
        ScoreFilter(MIN_SCORE),
        MonthlyProfitFilter(MIN_MONTHLY_PROFIT),
        DurationUnitFilter(DurationUnit.MONTH),  # TODO: Figure out how to compare days and months to remove this filter
    ]
    funding_requests = _filter_funding_requests(funding_requests, *filters)
    logger.info(f"Found {len(funding_requests)} available funding requests")

    funding_requests = run(gather_full_funding_requests(funding_requests))

    funding_requests = _filter_funding_requests(funding_requests, DicomFilter())
    if configuration.filter_notified:
        funding_requests = _filter_funding_requests(funding_requests, NotificationFilter(notifications))

    funding_requests.sort(key=lambda x: x.monthly_profit_rate, reverse=True)
    logger.debug(f"Finish sorting {len(funding_requests)} funding requests by monthly profit rate")

    return funding_requests


async def gather_full_funding_requests(funding_requests: list[FundingRequest]) -> list[FundingRequest]:
    """
    Gathers all the information and returns all the available funding requests.
    """
    tasks = []
    async with ClientSession() as session:
        for funding_request in funding_requests:
            tasks.append(ensure_future(get_credit_history(session, funding_request.id)))

        logger.info(f"Gathering {len(tasks)} credit history responses...")
        credit_histories = await gather(*tasks)
        for funding_request, credit_history in zip(funding_requests, credit_histories):
            funding_request.borrower.history = credit_history

    funding_requests = list(filter(lambda x: x.borrower.history, funding_requests))
    logger.info(f"Got {len(funding_requests)} funding requests with credit history")
    return funding_requests


@retry(KeyError, tries=5, delay=1)
def get_available_funding_requests() -> list[FundingRequest]:
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


async def get_credit_history(session: ClientSession, id_: int) -> CreditHistory | None:
    """
    Queries the Cumplo API and returns the credit history data from a given funding request's payer
    """
    logger.info(f"Getting credit history from funding request {id_}")
    async with session.get(f"{CUMPLO_FUNDING_REQUESTS_API}/{id_}") as response:
        text = await response.text()
        soup = BeautifulSoup(text, "html.parser")

        if CREDIT_DETAIL_TITLE not in (content := clean_text(soup.get_text())):
            logger.warning(f"Couldn't get credit history from funding request {id_}")
            return None

        logger.debug(f"Extracting credit history from funding request {id_} response")
        history = soup.select("span.loan-view-optional-visibility + span")

        return CreditHistory(
            average_deliquent_days=_extract_history_data(history[0]),
            paid_in_time=_extract_history_data(history[1]),
            dicom=DICOM_STRING in content,
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
