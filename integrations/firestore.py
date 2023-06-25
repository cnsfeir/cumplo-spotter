import os
from logging import getLogger
from typing import Any

import arrow
from dotenv import load_dotenv
from firebase_admin import credentials, firestore, initialize_app
from google.cloud.firestore_v1.collection import CollectionReference
from google.cloud.firestore_v1.document import DocumentReference
from starlette.exceptions import HTTPException

from models.notification import Notification
from models.user import User

load_dotenv()
logger = getLogger(__name__)

NOTIFICATIONS_COLLECTION = os.getenv("NOTIFICATIONS_COLLECTION", "notifications")
CONFIGURATIONS_COLLECTION = os.getenv("CONFIGURATIONS_COLLECTION", "configurations")
USERS_COLLECTION = os.getenv("USERS_COLLECTION", "users")
PROJECT_ID = os.getenv("PROJECT_ID", "")
SANTIAGO_TIMEZONE = "America/Santiago"


class Singleton(type):
    _instances: dict = {}

    def __call__(cls, *args: Any, **kwargs: Any) -> Any:
        """
        Creates a singleton instance of the class
        """
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance

        return cls._instances[cls]


class FirestoreClient(metaclass=Singleton):
    """
    Singleton class that initializes and returns a Firestore client
    """

    def __init__(self) -> None:
        firebase_credentials = credentials.ApplicationDefault()
        initialize_app(firebase_credentials, {"projectId": PROJECT_ID})
        self.client = firestore.client()

    def _get_user_document(self, id_user: str) -> DocumentReference:
        """Gets a user document reference"""
        return self.client.collection(USERS_COLLECTION).document(id_user)

    def _get_notification_document(self, id_user: str, id_funding_request: int) -> DocumentReference:
        """Gets a notification document reference"""
        user_document = self._get_user_document(id_user)
        return user_document.collection(NOTIFICATIONS_COLLECTION).document(str(id_funding_request))

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

    def get_user(self, id_user: str) -> User:
        """
        Gets the user data
        """
        logger.info(f"Getting user {id_user} from Firestore")
        user = self._get_user_document(id_user).get()

        if not user.exists:
            raise KeyError(f"User {id_user} does not exist")

        if not (user_data := user.to_dict()):
            raise ValueError(f"User {id_user} data is empty")

        configurations = self._get_user_configurations(id_user)
        notifications = self._get_user_notifications(id_user)
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

    def delete_notification(self, id_user: str, id_funding_request: int) -> None:
        """
        Deletes a notification of a funding request for a given user
        """
        logger.info(f"Deleting notification {id_funding_request} from Firestore")
        notification = self._get_notification_document(id_user, id_funding_request)
        notification.delete()


firestore_client = FirestoreClient()
