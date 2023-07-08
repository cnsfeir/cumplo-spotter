from http import HTTPStatus
from logging import getLogger
from typing import cast

from fastapi import APIRouter
from fastapi.requests import Request

from integrations import cumplo
from models.funding_request import FundingRequest
from models.user import User

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


@internal.post(path="/filter", status_code=HTTPStatus.OK)
async def filter_funding_requests(request: Request, funding_requests: list[FundingRequest]) -> list[FundingRequest]:
    """
    Filters a list of funding requests based on the user's configuration.
    """
    user = cast(User, request.state.user)

    promising_funding_requests = set()
    for configuration in user.configurations.values():
        promising_funding_requests.update(cumplo.filter_funding_requests(funding_requests, user, configuration))

    return list(promising_funding_requests)
