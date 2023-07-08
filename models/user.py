# pylint: disable=no-member

from datetime import datetime

import arrow
from pydantic import BaseModel, Field

from models.notification import Notification

from utils.constants import SANTIAGO_TIMEZONE


class User(BaseModel):
    id: str = Field(...)
    name: str = Field(...)
    calls: int = Field(...)
    last_call: datetime = Field(...)
    notifications: dict[int, Notification] = Field(default_factory=dict, exclude=True)

    def register_call(self) -> None:
        """Registers the last call date for a user"""
        self.last_call = arrow.now(SANTIAGO_TIMEZONE).datetime
        self.calls += 1
