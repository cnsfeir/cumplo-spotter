# pylint: disable=no-member

from http import HTTPStatus
from logging import getLogger
from typing import cast

from cumplo_common.models.user import User
from fastapi import APIRouter
from fastapi.requests import Request

from cumplo_spotter.business import funding_requests

logger = getLogger(__name__)


router = APIRouter(prefix="/funding-requests")


@router.get("", status_code=HTTPStatus.OK)
def _get_funding_requests(_request: Request) -> list[dict]:
    """
    Gets a list of available funding requests
    """
    available_funding_requests = funding_requests.get_available()
    return [funding_request.json() for funding_request in available_funding_requests]


@router.get("/promising", status_code=HTTPStatus.OK)
def _get_promising_funding_requests(request: Request) -> list[dict]:
    """
    Gets a list of promising funding requests based on the user's configuration
    """
    user = cast(User, request.state.user)
    promising_funding_requests = funding_requests.get_promising(user)
    return [request.json() for request in promising_funding_requests]
