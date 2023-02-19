from logging import getLogger

from flask import Flask, Response, request

import main

logger = getLogger(__name__)
app = Flask(__name__)


@app.route("/get_investment_opportunities", methods=["POST"])
def test_get_investment_opportunities() -> Response:
    """
    [Endpoint for local development]
    Gets a list of good investment opportunities.
    """
    return main.get_investment_opportunities(request)
