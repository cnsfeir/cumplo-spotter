from http import HTTPStatus
from logging import getLogger
from typing import cast

from cumplo_common.integrations.cloud_pubsub import CloudPubSub
from cumplo_common.models import PrivateEvent, User
from fastapi import APIRouter
from fastapi.requests import Request

from cumplo_spotter.business import funding_requests
from cumplo_spotter.integrations import cumplo

logger = getLogger(__name__)

router = APIRouter(prefix="/funding-requests")


@router.post(path="/fetch", status_code=HTTPStatus.NO_CONTENT)
def _fetch_funding_requests(request: Request) -> None:
    """Fetch a list of funding requests and emits an event containing them."""
    user = cast(User, request.state.user)

    cumplo.cache.clear()
    available_funding_requests = funding_requests.get_available()
    logger.info(f"Found {len(available_funding_requests)} available funding requests")

    if content := [funding_request.json() for funding_request in available_funding_requests]:
        CloudPubSub.publish(content=content, topic=PrivateEvent.FUNDING_REQUEST_AVAILABLE, id_user=str(user.id))
