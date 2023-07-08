from http import HTTPStatus
from logging import getLogger

from fastapi import APIRouter
from fastapi.requests import Request

from integrations.cumplo import get_available_funding_requests
from models.funding_request import FundingRequest

logger = getLogger(__name__)

router = APIRouter(prefix="/funding-requests")


@router.get("", status_code=HTTPStatus.OK)
async def get_funding_requests(_request: Request) -> list[FundingRequest]:
    """
    Gets a list of available funding requests.
    """
    funding_requests = get_available_funding_requests()
    return funding_requests


@router.get("/promising", status_code=HTTPStatus.OK)
async def get_promising_funding_requests(_request: Request) -> list[FundingRequest]:
    """
    Gets a list of promising funding requests based on the user's configuration.
    """
    funding_requests = get_available_funding_requests()
    # TODO: Filter funding requests based on ALL of user's configurations
    return funding_requests
