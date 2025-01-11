from http import HTTPStatus
from logging import getLogger
from typing import cast

from cumplo_common.database import firestore
from cumplo_common.models.user import User
from fastapi import APIRouter
from fastapi.requests import Request

logger = getLogger(__name__)


router = APIRouter(prefix="/users")


@router.post("/filters", status_code=HTTPStatus.OK)
def _clear_users_cache(request: Request) -> None:
    """Clear a specific user from the Firestore cache so it can be updated."""
    user = cast(User, request.state.user)
    firestore.users.cache.remove(id_user=user.id, api_key=user.api_key)
