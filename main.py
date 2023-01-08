import json
import logging

import functions_framework
from flask import Request, Response, make_response

from integrations.cumplo import get_funding_requests

logging.basicConfig(level=logging.DEBUG, format="\n [%(levelname)s] (%(name)s:%(lineno)d) \n %(message)s")
logger = logging.getLogger(__name__)


@functions_framework.http
def get_investment_oportunities(request: Request) -> Response:
    """
    Gets a list of investment oportunities and sends it to the user via email
    """
    data = json.loads(request.data)
    funding_requests = get_funding_requests(**data)
    result = [funding_request.dict() for funding_request in funding_requests]
    return make_response(result, 200)
