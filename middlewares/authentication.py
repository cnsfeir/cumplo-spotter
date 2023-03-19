import os
from collections.abc import Callable

from dotenv import load_dotenv
from flask import Request, Response

from exceptions.http import ForbiddenException
from integrations.firestore import firestore_client
from models.user import User

load_dotenv()

API_KEY = os.getenv("API_KEY")


def authenticate(function_: Callable[[Request, User], Response]) -> Callable[[Request], Response]:
    """
    Authenticates a request.
    """

    def authenticator(request: Request) -> Response:
        id_user = request.headers.get("X-API-KEY", "")
        try:
            user = firestore_client.get_user(id_user)
        except KeyError as error:
            raise ForbiddenException() from error

        firestore_client.register_call(user)
        return function_(request, user)

    return authenticator
