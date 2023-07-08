from http import HTTPStatus
from logging import getLogger
from typing import cast

from fastapi import APIRouter
from fastapi.exceptions import HTTPException
from fastapi.requests import Request

from integrations.firestore import firestore_client
from models.configuration import Configuration
from models.user import User
from schemas.configurations import ConfigurationPayload
from utils.constants import MAX_CONFIGURATIONS

logger = getLogger(__name__)

router = APIRouter(prefix="/configurations")


@router.get("", status_code=HTTPStatus.OK)
async def get_configurations(request: Request) -> dict[int, Configuration]:
    """
    Gets a list of available funding requests.
    """
    user = cast(User, request.state.user)
    return user.configurations


@router.get("/{id_configuration}", status_code=HTTPStatus.OK)
async def get_single_configurations(request: Request, id_configuration: int) -> Configuration:
    """
    Gets a list of available funding requests.
    """
    user = cast(User, request.state.user)
    if configuration := user.configurations.get(id_configuration):
        return configuration

    raise HTTPException(status_code=HTTPStatus.NOT_FOUND)


@router.post("", status_code=HTTPStatus.CREATED)
async def post_configuration(request: Request, payload: ConfigurationPayload) -> Configuration:
    """
    Creates a configuration.
    """
    user = cast(User, request.state.user)
    if len(user.configurations) >= MAX_CONFIGURATIONS:
        raise HTTPException(status_code=HTTPStatus.TOO_MANY_REQUESTS, detail="Max configurations reached")

    if payload in user.configurations.values():
        raise HTTPException(status_code=HTTPStatus.CONFLICT, detail="Configuration already exists")

    configuration = Configuration(**payload.dict())
    firestore_client.update_configuration(user.id, configuration)
    return configuration


@router.put("/{id_configuration}", status_code=HTTPStatus.NO_CONTENT)
async def put_configuration(request: Request, payload: ConfigurationPayload, id_configuration: int) -> None:
    """
    Creates or updates a configuration.
    """
    user = cast(User, request.state.user)
    if configuration := user.configurations.get(id_configuration):
        configuration = configuration.copy(update=payload.dict())
        return firestore_client.update_configuration(user.id, configuration)

    raise HTTPException(status_code=HTTPStatus.NOT_FOUND)