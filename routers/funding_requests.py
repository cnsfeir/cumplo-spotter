from http import HTTPStatus
from logging import getLogger
from typing import cast

from fastapi import APIRouter
from fastapi.requests import Request

from integrations import cumplo
from integrations.firestore import firestore_client
from models.funding_request import FundingRequest
from models.user import User
from schemas.funding_requests import FilterFundingRequestPayload

logger = getLogger(__name__)

router = APIRouter(prefix="/funding-requests")
internal = APIRouter(prefix="/funding-requests")


@router.get("", status_code=HTTPStatus.OK)
async def get_funding_requests(_request: Request) -> list[FundingRequest]:
    """
    Gets a list of available funding requests.
    """
    funding_requests = cumplo.get_available_funding_requests()
    return funding_requests


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
        # TODO: Schedule a taks to filter the funding requests and send webhooks
        pass


@internal.post(path="/filter", status_code=HTTPStatus.OK)
async def filter_funding_requests(_request: Request, payload: FilterFundingRequestPayload) -> None:
    """
    Filters a list of funding requests based on the user's configuration.
    """
    user = firestore_client.get_user(payload.id_user)

    promising_funding_requests = set()
    for configuration in user.configurations.values():
        promising_funding_requests.update(cumplo.filter_funding_requests(payload.funding_requests, user, configuration))

    # TODO: Send webhooks
