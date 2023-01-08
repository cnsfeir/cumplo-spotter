import os
from collections.abc import Callable

from dotenv import load_dotenv
from flask import Request, Response

from exceptions.http import ForbiddenException

load_dotenv()

API_KEY = os.getenv("API_KEY")


def authenticate(function_: Callable[[Request], Response]) -> Callable[[Request], Response]:
    """
    Authenticates a request.
    """

    def authenticator(request: Request) -> Response:
        if request.headers.get("X-API-KEY") != API_KEY:
            raise ForbiddenException()
        return function_(request)

    return authenticator
