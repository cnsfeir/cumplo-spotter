# pylint: disable=raise-missing-from

import os
from http import HTTPStatus

from dotenv import load_dotenv
from fastapi import Header
from fastapi.exceptions import HTTPException
from fastapi.requests import Request

from integrations.firestore import firestore_client

load_dotenv()

API_KEY = os.getenv("API_KEY")


async def athenticate(request: Request, x_api_key: str = Header()) -> None:
    """
    Authenticates a request.
    """
    if not x_api_key:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED)

    try:
        user = firestore_client.get_user(x_api_key)
    except (KeyError, ValueError):
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED)

    user.register_call()
    firestore_client.update_user(user)

    request.state.user = user
