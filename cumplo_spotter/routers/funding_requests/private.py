# pylint: disable=no-member

from http import HTTPStatus
from logging import getLogger
from typing import cast

from cumplo_common.integrations.cloud_pubsub import publish_event
from cumplo_common.models.funding_request import FundingRequest
from cumplo_common.models.user import User
from fastapi import APIRouter
from fastapi.requests import Request

from cumplo_spotter.business import funding_requests
from cumplo_spotter.utils.constants import AVAILABLE_FUNDING_REQUESTS_TOPIC, PROMISING_FUNDING_REQUESTS_TOPIC

logger = getLogger(__name__)

router = APIRouter(prefix="/funding-requests")


@router.post(path="/fetch", status_code=HTTPStatus.NO_CONTENT)
def _fetch_funding_requests(request: Request) -> None:
    """
    Fetches a list of funding requests and emits an event containing them.
    """
    user = cast(User, request.state.user)

    available_funding_requests = funding_requests.get_available()
    logger.info(f"Found {len(available_funding_requests)} available funding requests")

    if content := [funding_request.json() for funding_request in available_funding_requests]:
        publish_event(content, AVAILABLE_FUNDING_REQUESTS_TOPIC, id_user=str(user.id))


@router.post(path="/filter", status_code=HTTPStatus.NO_CONTENT)
def _filter_funding_requests(request: Request, payload: list[FundingRequest]) -> None:
    """
    Filters a list of funding requests based on the user's filters.
    """
    user = cast(User, request.state.user)

    promising_funding_requests = set()
    for filters in user.filters.values():
        promising_funding_requests.update(funding_requests.filter_(list(payload), filters))

    if not promising_funding_requests:
        logger.info(f"No promising funding requests for user {user.id}")
        return

    logger.info(f"Found {len(promising_funding_requests)} promising funding requests for user {user.id}")

    for funding_request in promising_funding_requests:
        logger.info(f"Notifying about funding request {funding_request.id} to user {user.id}")
        publish_event(funding_request.json(), PROMISING_FUNDING_REQUESTS_TOPIC, id_user=str(user.id))
