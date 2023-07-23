from http import HTTPStatus
from logging import getLogger
from typing import Annotated, cast

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
async def get_configurations(request: Request) -> list[Annotated[dict, Configuration]]:
    """
    Gets a list of existing configurations.
    """
    user = cast(User, request.state.user)
    return [configuration.serialize() for configuration in user.configurations.values()]


@router.get("/{id_configuration}", status_code=HTTPStatus.OK)
async def get_single_configurations(request: Request, id_configuration: int) -> Annotated[dict, Configuration]:
    """
    Gets a single configuration.
    """
    user = cast(User, request.state.user)
    if configuration := user.configurations.get(id_configuration):
        return configuration.serialize()

    raise HTTPException(status_code=HTTPStatus.NOT_FOUND)


@router.post("", status_code=HTTPStatus.CREATED)
async def post_configuration(request: Request, payload: ConfigurationPayload) -> Annotated[dict, Configuration]:
    """
    Creates a configuration.
    """
    user = cast(User, request.state.user)
    if len(user.configurations) >= MAX_CONFIGURATIONS:
        raise HTTPException(status_code=HTTPStatus.TOO_MANY_REQUESTS, detail="Max configurations reached")

    id_configuration = max(user.configurations.keys(), default=0) + 1
    configuration = Configuration(id=id_configuration, **payload.dict(exclude_none=True))

    if configuration in user.configurations.values():
        raise HTTPException(status_code=HTTPStatus.CONFLICT, detail="Configuration already exists")

    firestore_client.update_configuration(user.id, configuration)
    return configuration.serialize()


@router.put("/{id_configuration}", status_code=HTTPStatus.NO_CONTENT)
async def put_configuration(request: Request, payload: ConfigurationPayload, id_configuration: int) -> None:
    """
    Updates a configuration.
    """
    user = cast(User, request.state.user)
    if configuration := user.configurations.get(id_configuration):
        configuration = configuration.copy(update=payload.dict())
        return firestore_client.update_configuration(user.id, configuration)

    raise HTTPException(status_code=HTTPStatus.NOT_FOUND)


@router.delete("/{id_configuration}", status_code=HTTPStatus.NO_CONTENT)
async def delete_configuration(request: Request, id_configuration: int) -> None:
    """
    Deletes a configuration.
    """
    user = cast(User, request.state.user)
    if configuration := user.configurations.get(id_configuration):
        return firestore_client.delete_configuration(user.id, configuration.id)

    raise HTTPException(status_code=HTTPStatus.NOT_FOUND)
