from logging import getLogger

from fastapi import APIRouter
from fastapi.requests import Request
from fastapi.responses import JSONResponse

from integrations.cumplo import get_available_funding_requests

logger = getLogger(__name__)

router = APIRouter(prefix="/funding-requests")


@router.get("")
async def get_funding_requests(_request: Request) -> JSONResponse:
    """
    Gets a list of available funding requests.
    """
    funding_requests = get_available_funding_requests()
    return JSONResponse(status_code=200, content=funding_requests)


@router.get("/promising")
async def get_promising_funding_requests(_request: Request) -> JSONResponse:
    """
    Gets a list of promising funding requests based on the user's configuration.
    """
    funding_requests = get_available_funding_requests()
    # TODO: Filter funding requests based on ALL of user's configurations
    return JSONResponse(status_code=200, content=funding_requests)
