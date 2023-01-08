import json

from flask import Request


def get_investment_oportunities_context(request: Request) -> tuple[int, float, int]:
    """
    Gets the min profit rate, min borrower score and max deliquent days
    """
    data = json.loads(request.data)
    return data["max_profit_rate"], data["min_borrower_score"], data["max_deliquent_days"]
