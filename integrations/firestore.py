import os
from logging import getLogger
from typing import Any

import arrow
from dotenv import load_dotenv
from firebase_admin import credentials, firestore, initialize_app
from google.cloud.firestore_v1.document import DocumentReference
from starlette.exceptions import HTTPException

from models.notification import Notification
from models.user import User

load_dotenv()
logger = getLogger(__name__)

NOTIFICATIONS_COLLECTION = os.getenv("NOTIFICATIONS_COLLECTION", "notifications")
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

    def get_user_document(self, id_user: str) -> DocumentReference:
        """Gets the user document reference"""
        return self.client.collection(USERS_COLLECTION).document(str(id_user))

    def get_notification_document(self, id_user: str, id_funding_request: int) -> DocumentReference:
        """Gets the notification document reference"""
        user_document = self.get_user_document(id_user)
        return user_document.collection(NOTIFICATIONS_COLLECTION).document(str(id_funding_request))

    def get_notifications(self, id_user: str) -> dict[int, Notification]:
        """
        Gets the dictionary of funding requests that have already been notified
        """
        logger.info(f"Getting user {id_user} notifications from Firestore")
        notifications = self.get_user_document(id_user).collection(NOTIFICATIONS_COLLECTION).stream()
        return {int(n.id): Notification(id=int(n.id), **n.to_dict()) for n in notifications}

    def set_notification_date(self, id_user: str, id_funding_request: int) -> None:
        """
        Sets the notification date for a funding request
        """
        content = {"date": arrow.now(SANTIAGO_TIMEZONE).datetime}
        self.get_notification_document(id_user, id_funding_request).set(content)

    def delete_notification(self, id_user: str, id_funding_request: int) -> None:
        """
        Deletes a notification
        """
        logger.info(f"Deleting notification {id_funding_request} from Firestore")
        self.get_notification_document(id_user, id_funding_request).delete()

    def get_user(self, id_user: str) -> User:
        """
        Gets the user data
        """
        logger.info(f"Getting user {id_user} from Firestore")
        user = self.get_user_document(id_user).get()

        if not user.exists:
            raise HTTPException(status_code=404, detail=f"User {id_user} does not exist")

        if not (user_data := user.to_dict()):
            raise HTTPException(status_code=500, detail=f"User {id_user} data is empty")

        notifications = self.get_notifications(id_user)
        return User(id=user.id, notifications=notifications, **user_data)

    def register_call(self, user: User) -> None:
        """
        Sets the last call date for a user
        """
        logger.info(f"Registering call from user {user.id} to Firestore")
        content = user.build_new_call()
        self.get_user_document(user.id).set(content)


firestore_client = FirestoreClient()
