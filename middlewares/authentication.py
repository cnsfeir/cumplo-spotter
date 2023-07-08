# pylint: disable=raise-missing-from

import os
import re
from http import HTTPStatus
from typing import Annotated

from dotenv import load_dotenv
from fastapi import Header
from fastapi.exceptions import HTTPException
from fastapi.requests import Request

from integrations.firestore import firestore_client

load_dotenv()

API_KEY = os.getenv("API_KEY")


async def athenticate(request: Request, x_envoy_original_path: Annotated[str | None, Header()] = None) -> None:
    """
    Authenticates a request.
    """
    if not x_envoy_original_path:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED)

    pattern = r"\?key=([^&]+)"
    if not (match := re.search(pattern, x_envoy_original_path)):
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED)

    try:
        api_key = match.group(1)
        user = firestore_client.get_user(api_key)
    except (KeyError, ValueError):
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED)

    user.register_call()
    firestore_client.update_user(user)

    request.state.user = user
