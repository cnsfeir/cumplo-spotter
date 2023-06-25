from logging import getLogger

from fastapi import APIRouter
from fastapi.responses import JSONResponse

logger = getLogger(__name__)

router = APIRouter(prefix="/funding-requests")


@router.get("")
async def get_funding_requests() -> JSONResponse:
    """
    Gets a list of funding requests.
    """
    logger.info(f"Getting investment opportunities for {user.name} ({user.id})")
    configuration = get_configuration(request)

    logger.info(f"Got this configuration for {user.name}: {configuration.dict(exclude_none=True)}")
    funding_requests = get_funding_requests(user, configuration)
    result = {
        "total": len(funding_requests),
        "ids": [funding_request.id for funding_request in funding_requests],
        "opportunities": {
            funding_request.id: funding_request.dict(exclude_none=True) for funding_request in funding_requests
        },
    }
    return make_response(result, 200)
