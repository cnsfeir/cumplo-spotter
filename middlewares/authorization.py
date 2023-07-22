# pylint: disable=raise-missing-from

from http import HTTPStatus

from fastapi.exceptions import HTTPException
from fastapi.requests import Request


async def is_admin(request: Request) -> None:
    """
    Authenticates that the user is admin
    """
    user = request.state.user
    if not user.is_admin:
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN)
