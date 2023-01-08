import json
import logging

import functions_framework
from flask import Request, Response

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
    for funding_request in funding_requests:
        print(funding_request)

    return Response(status=200)
