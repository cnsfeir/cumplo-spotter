import logging

import functions_framework
from flask import Request, Response, make_response

from integrations.cumplo import get_funding_requests
from middlewares.authentication import authenticate

logging.basicConfig(level=logging.DEBUG, format="\n [%(levelname)s] (%(name)s:%(lineno)d) \n %(message)s")
logger = logging.getLogger(__name__)


@authenticate
@functions_framework.http
def get_investment_opportunities(_request: Request) -> Response:
    """
    Gets a list of good investment opportunities.
    """
    funding_requests = get_funding_requests()
    result = {
        "total": len(funding_requests),
        "ids": [funding_request.id for funding_request in funding_requests],
        "opportunities": [funding_request.dict() for funding_request in funding_requests],
    }
    return make_response(result, 200)
