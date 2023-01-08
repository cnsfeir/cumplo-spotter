import logging

import functions_framework
from flask import Request, Response, make_response

from integrations.cumplo import get_funding_requests

logging.basicConfig(level=logging.DEBUG, format="\n [%(levelname)s] (%(name)s:%(lineno)d) \n %(message)s")
logger = logging.getLogger(__name__)


@functions_framework.http
def get_investment_opportunities(_request: Request) -> Response:
    """
    Gets a list of good investment opportunities.
    """
    funding_requests = get_funding_requests()
    result = [funding_request.dict() for funding_request in funding_requests]
    return make_response(result, 200)


@functions_framework.http
def count_investment_opportunities(_request: Request) -> Response:
    """
    Returns the total amount of good investment opportunities.
    """
    funding_requests = get_funding_requests()
    return make_response({"count": len(funding_requests)}, 200)
