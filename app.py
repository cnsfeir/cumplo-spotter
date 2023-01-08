from logging import getLogger

from flask import Flask, Response, request

import main

logger = getLogger(__name__)
app = Flask(__name__)


@app.route("/investment_oportunities")
def get_investment_oportunities() -> Response:
    """
    [Endpoint for local development]
    Gets a list of good investment oportunities.
    """
    return main.get_investment_oportunities(request)


@app.route("/investment_oportunities/count")
def count_investment_oportunities() -> Response:
    """
    [Endpoint for local development]
    Returns the total amount of good investment oportunities.
    """
    return main.count_investment_oportunities(request)
