from collections.abc import Generator
from logging import getLogger

import arrow
from dotenv import load_dotenv
from firebase_admin import credentials, firestore, initialize_app
from google.cloud.firestore_v1.document import DocumentReference

from models.configuration import Configuration
from models.notification import Notification
from models.user import User
from utils.constants import (
    CONFIGURATIONS_COLLECTION,
    NOTIFICATIONS_COLLECTION,
    PROJECT_ID,
    SANTIAGO_TIMEZONE,
    USERS_COLLECTION,
)
from utils.text import secure_key

load_dotenv()
logger = getLogger(__name__)


class FirestoreClient:
    """
    Singleton class that initializes and returns a Firestore client
    """

    def __init__(self) -> None:
        firebase_credentials = credentials.ApplicationDefault()
        initialize_app(firebase_credentials, {"projectId": PROJECT_ID})
        self.client = firestore.client()

    def get_users(self) -> Generator[User, None, None]:
        """
        Gets all the users data
        """
        logger.info("Getting all users from Firestore")
        user_stream = self.client.collection(USERS_COLLECTION).stream()
        for user in user_stream:
            yield User(id=user.id, **user.to_dict())

    def get_user(self, api_key: str) -> User:
        """
        Gets the user data
        """
        logger.info(f"Getting user with API key {secure_key(api_key)} from Firestore")
        user_stream = self.client.collection(USERS_COLLECTION).where("api_key", "==", api_key).stream()

        if not (user := next(user_stream, None)):
            raise KeyError(f"User with API key {secure_key(api_key)} does not exist")

        if not (user_data := user.to_dict()):
            raise ValueError(f"User with API key {secure_key(api_key)} data is empty")

        configurations = self._get_user_configurations(user.id)
        notifications = self._get_user_notifications(user.id)
        return User(id=user.id, configurations=configurations, notifications=notifications, **user_data)

    def update_user(self, user: User) -> None:
        """
        Updates the user data
        """
        logger.info(f"Updating user {user.id} at Firestore")
        user_document = self._get_user_document(user.id)
        user_document.set(user.dict())

    def set_notification_date(self, id_user: str, id_funding_request: int) -> None:
        """
        Sets the notification date of a funding request for a given user
        """
        logger.info(f"Setting notification date for funding request {id_funding_request} at Firestore")
        notification = self._get_notification_document(id_user, id_funding_request)
        notification.set({"date": arrow.now(SANTIAGO_TIMEZONE).datetime})

    def update_configuration(self, id_user: str, configuration: Configuration) -> None:
        """
        Updates a configuration of a user
        """
        logger.info(f"Updating configuration {configuration.id} of user {id_user} at Firestore")
        configuration_reference = self._get_configuration_document(id_user, configuration.id)
        configuration_reference.set(configuration.dict(exclude_none=True))

    def delete_notification(self, id_user: str, id_funding_request: int) -> None:
        """
        Deletes a notification of a funding request for a given user
        """
        logger.info(f"Deleting notification {id_funding_request} from Firestore")
        notification = self._get_notification_document(id_user, id_funding_request)
        notification.delete()

    def _get_user_document(self, id_user: str) -> DocumentReference:
        """Gets a user document reference"""
        return self.client.collection(USERS_COLLECTION).document(id_user)

    def _get_notification_document(self, id_user: str, id_funding_request: int) -> DocumentReference:
        """Gets a notification document reference"""
        user_document = self._get_user_document(id_user)
        return user_document.collection(NOTIFICATIONS_COLLECTION).document(str(id_funding_request))

    def _get_configuration_document(self, id_user: str, id_configuration: int) -> DocumentReference:
        """Gets a configuration document reference"""
        user_document = self._get_user_document(id_user)
        return user_document.collection(CONFIGURATIONS_COLLECTION).document(str(id_configuration))

    def _get_user_notifications(self, id_user: str) -> dict[int, Notification]:
        """
        Gets the user notifications data
        """
        logger.info(f"Getting user {id_user} notifications from Firestore")
        user_document = self._get_user_document(id_user)
        notifications = user_document.collection(NOTIFICATIONS_COLLECTION).stream()
        return {int(n.id): Notification(id=int(n.id), **n.to_dict()) for n in notifications}

    def _get_user_configurations(self, id_user: str) -> dict[int, Configuration]:
        """
        Gets the user configurations data
        """
        logger.info(f"Getting user {id_user} configurations from Firestore")
        user_document = self._get_user_document(id_user)
        configurations = user_document.collection(CONFIGURATIONS_COLLECTION).stream()
        return {int(n.id): Configuration(id=int(n.id), **n.to_dict()) for n in configurations}


firestore_client = FirestoreClient()
