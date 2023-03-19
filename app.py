# pylint: disable=no-value-for-parameter

from logging import getLogger

from flask import Flask, Response, request

import main

logger = getLogger(__name__)
app = Flask(__name__)


@app.route("/fetch-investment-opportunities", methods=["POST"])
def test_fetch_investment_opportunities() -> Response:
    """
    [Endpoint for local development]
    Gets a list of good investment opportunities.
    """
    return main.fetch_investment_opportunities(request)  # type: ignore
