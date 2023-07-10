from http import HTTPStatus
from logging import getLogger
from typing import cast

from fastapi import APIRouter
from fastapi.requests import Request

from integrations import cumplo
from integrations.cloud_tasks import create_http_task
from integrations.firestore import firestore_client
from models.funding_request import FundingRequest
from models.user import User
from schemas.funding_requests import FilterFundingRequestPayload
from utils.constants import FILTER_FUNDING_REQUESTS_QUEUE, FUNDING_REQUESTS_URL, WEBHOOK_QUEUE

logger = getLogger(__name__)

router = APIRouter(prefix="/funding-requests")
internal = APIRouter(prefix="/funding-requests")


# TODO: Add a limit for the number of daily calls per user at a middleware level
@router.get("", status_code=HTTPStatus.OK)
async def get_funding_requests(_request: Request) -> list[FundingRequest]:
    """
    Gets a list of available funding requests.
    """
    funding_requests = cumplo.get_available_funding_requests()
    return funding_requests


# TODO: Add a limit for the number of daily calls per user at a middleware level
@router.get("/promising", status_code=HTTPStatus.OK)
async def get_promising_funding_requests(request: Request) -> list[FundingRequest]:
    """
    Gets a list of promising funding requests based on the user's configuration.
    """
    funding_requests = cumplo.get_available_funding_requests()
    user = cast(User, request.state.user)

    promising_funding_requests = set()
    for configuration in user.configurations.values():
        promising_funding_requests.update(cumplo.filter_funding_requests(funding_requests, user, configuration))

    return list(promising_funding_requests)


@internal.post(path="/fetch", status_code=HTTPStatus.OK)
async def fetch_funding_requests(_request: Request) -> None:
    """
    Fetches a list of funding requests and schedules the filtering process.
    """
    funding_requests = cumplo.get_available_funding_requests()

    for user in firestore_client.get_users():
        if not user.webhook_url:
            logger.info(f"User {user.id} does not have a webhook URL configured. Skipping")
            continue

        payload = FilterFundingRequestPayload(id_user=user.id, funding_requests=funding_requests)
        create_http_task(
            url=f"{FUNDING_REQUESTS_URL}/filter", payload=payload.dict(), queue=FILTER_FUNDING_REQUESTS_QUEUE
        )


@internal.post(path="/filter", status_code=HTTPStatus.OK)
async def filter_funding_requests(_request: Request, payload: FilterFundingRequestPayload) -> None:
    """
    Filters a list of funding requests based on the user's configuration.
    """
    user = firestore_client.get_user(payload.id_user)

    promising_funding_requests = set()
    for configuration in user.configurations.values():
        promising_funding_requests.update(cumplo.filter_funding_requests(payload.funding_requests, user, configuration))

    if not promising_funding_requests:
        logger.info(f"No promising funding requests for user {user.id}")
        return

    logger.info(f"Found {len(promising_funding_requests)} promising funding requests for user {user.id}")
    body = {funding_request.id: funding_request.dict() for funding_request in promising_funding_requests}

    assert user.webhook_url, f"User {user.id} does not have a webhook URL configured"
    create_http_task(url=user.webhook_url, payload=body, queue=WEBHOOK_QUEUE)
