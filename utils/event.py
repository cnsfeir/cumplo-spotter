import json

from flask import Request

from models.configuration import Configuration


def get_configuration(request: Request) -> Configuration:
    """
    Gets the configuration from the request.
    """
    data = json.loads(request.data)
    return Configuration(**data)
