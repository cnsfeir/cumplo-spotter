import logging
import os

import functions_framework
from flask import Request, Response, make_response

from integrations.cumplo import get_funding_requests
from middlewares.authentication import authenticate
from utils.event import get_configuration

IS_TESTING = bool(os.getenv("IS_TESTING"))

FORMAT = "\n [%(levelname)s] (%(name)s:%(lineno)d) \n %(message)s" if IS_TESTING else "\n [%(levelname)s] %(message)s"
logging.basicConfig(level=logging.DEBUG, format=FORMAT)
logger = logging.getLogger(__name__)


@authenticate
@functions_framework.http
def get_investment_opportunities(request: Request) -> Response:
    """
    Gets a list of good investment opportunities.
    """
    configuration = get_configuration(request)
    funding_requests = get_funding_requests(configuration)
    result = {
        "total": len(funding_requests),
        "ids": [funding_request.id for funding_request in funding_requests],
        "opportunities": [funding_request.serialized() for funding_request in funding_requests],
    }
    return make_response(result, 200)
