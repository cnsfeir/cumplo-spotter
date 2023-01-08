import os
from typing import Any

from dotenv import load_dotenv
from firebase_admin import credentials, firestore, initialize_app

load_dotenv()

PROJECT_ID = os.getenv("PROJECT_ID", "")


def initialize_firestore_client() -> Any:
    """
    Initializes and returns a firestore client
    """
    firebase_credentials = credentials.ApplicationDefault()
    initialize_app(firebase_credentials, {"projectId": PROJECT_ID})
    return firestore.client()


db = initialize_firestore_client()
