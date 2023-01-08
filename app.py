from logging import getLogger

from flask import Flask, Response, request

import main

logger = getLogger(__name__)
app = Flask(__name__)


@app.route("/investment_opportunities")
def test_get_investment_opportunities() -> Response:
    """
    [Endpoint for local development]
    Gets a list of good investment opportunities.
    """
    return main.get_investment_opportunities(request)


@app.route("/investment_opportunities/count")
def test_count_investment_opportunities() -> Response:
    """
    [Endpoint for local development]
    Returns the total amount of good investment opportunities.
    """
    return main.count_investment_opportunities(request)
