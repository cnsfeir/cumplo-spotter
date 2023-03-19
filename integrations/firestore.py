import os
from logging import getLogger
from typing import Any

import arrow
from dotenv import load_dotenv
from firebase_admin import credentials, firestore, initialize_app

from models.notification import Notification
from models.user import User

load_dotenv()
logger = getLogger(__name__)

PROJECT_ID = os.getenv("PROJECT_ID", "")
SANTIAGO_TIMEZONE = "America/Santiago"
NOTIFICATIONS_COLLECTION = "notifications"
USERS_COLLECTION = "users"


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

    def get_notifications(self, id_user: str) -> dict[int, Notification]:
        """
        Gets the dictionary of funding requests that have already been notified
        """
        logger.info(f"Getting user {id_user} notifications from Firestore")
        notifications = (
            self.client.collection(USERS_COLLECTION)
            .document(str(id_user))
            .collection(NOTIFICATIONS_COLLECTION)
            .stream()
        )
        return {int(n.id): Notification(id=int(n.id), **n.to_dict()) for n in notifications}

    def set_notification_date(self, id_user: str, id_funding_request: int) -> None:
        """
        Sets the notification date for a funding request
        """
        content = {"date": arrow.now(SANTIAGO_TIMEZONE).datetime}
        user_document = self.client.collection(USERS_COLLECTION).document(str(id_user))
        user_document.collection(NOTIFICATIONS_COLLECTION).document(str(id_funding_request)).set(content)

    def delete_notification(self, id_funding_request: int) -> None:
        """
        Deletes a notification
        """
        logger.info(f"Deleting notification {id_funding_request} from Firestore")
        self.client.collection(NOTIFICATIONS_COLLECTION).document(str(id_funding_request)).delete()

    def get_user(self, id_user: str) -> User:
        """
        Gets the user data
        """
        logger.info(f"Getting user {id_user} from Firestore")
        user = self.client.collection(USERS_COLLECTION).document(str(id_user)).get()
        if not user.exists:
            raise KeyError(f"User {id_user} does not exist")

        notifications = self.get_notifications(id_user)
        return User(id=user.id, notifications=notifications, **user.to_dict())

    def register_call(self, user: User) -> None:
        """
        Sets the last call date for a user
        """
        logger.info(f"Registering call from user {user.id} to Firestore")
        content = user.build_new_call()
        self.client.collection(USERS_COLLECTION).document(str(user.id)).set(content)


firestore_client = FirestoreClient()
