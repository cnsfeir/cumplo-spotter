import os
from logging import CRITICAL, DEBUG, basicConfig, getLogger

import functions_framework
from flask import Request, Response, make_response

from integrations.cumplo import get_funding_requests
from middlewares.authentication import authenticate
from models.user import User
from utils.event import get_configuration

IS_TESTING = bool(os.getenv("IS_TESTING"))

FORMAT = "\n [%(levelname)s] (%(name)s:%(lineno)d) \n %(message)s" if IS_TESTING else "\n [%(levelname)s] %(message)s"
basicConfig(level=DEBUG, format=FORMAT)
logger = getLogger(__name__)

getLogger("google").setLevel(CRITICAL)
getLogger("urllib3").setLevel(CRITICAL)
getLogger("asyncio").setLevel(CRITICAL)
getLogger("fsevents").setLevel(CRITICAL)
getLogger("werkzeug").setLevel(CRITICAL)
getLogger("charset_normalizer").setLevel(CRITICAL)


@authenticate
@functions_framework.http
def fetch_investment_opportunities(request: Request, user: User) -> Response:
    """
    Fetches a list of good investment opportunities.
    """
    logger.info(f"Getting investment opportunities for {user.name} ({user.id})")
    configuration = get_configuration(request)

    logger.info(f"Got this configuration for {user.name}: {configuration}")
    funding_requests = get_funding_requests(user, configuration)
    result = {
        "total": len(funding_requests),
        "ids": [funding_request.id for funding_request in funding_requests],
        "opportunities": [funding_request.dict(exclude_none=True) for funding_request in funding_requests],
    }
    return make_response(result, 200)
