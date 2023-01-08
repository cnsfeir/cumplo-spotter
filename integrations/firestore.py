import os
from logging import getLogger
from typing import Any

import arrow
from dotenv import load_dotenv
from firebase_admin import credentials, firestore, initialize_app

from models.notification import Notification

load_dotenv()
logger = getLogger(__name__)

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

    notifications: dict[int, Notification] | None = None

    def __init__(self) -> None:
        firebase_credentials = credentials.ApplicationDefault()
        initialize_app(firebase_credentials, {"projectId": PROJECT_ID})
        self.client = firestore.client()
        self.notifications = self.get_notifications()

    def get_notifications(self) -> dict[int, Notification]:
        """
        Gets the dictionary of funding requests that have already been notified
        """
        if self.notifications:
            logger.info("Notifications already loaded.")
            return self.notifications

        logger.info("Getting notifications from Firestore...")
        notifications = self.client.collection("notifications").stream()
        return {int(n.id): Notification(id=int(n.id), **n.to_dict()) for n in notifications}

    def set_notification_date(self, id_funding_request: int) -> None:
        """
        Sets the notification date for a funding request
        """
        content = {"date": arrow.now(SANTIAGO_TIMEZONE).datetime}
        self.client.collection("notifications").document(str(id_funding_request)).set(content)

    def delete_notification(self, id_funding_request: int) -> None:
        """
        Sets the notification date for a funding request
        """
        self.client.collection("notifications").document(str(id_funding_request)).delete()


firestore_client = FirestoreClient()
