# pylint: disable=no-member

from datetime import datetime

import arrow
from pydantic import BaseModel, Field

from models.notification import Notification

SANTIAGO_TIMEZONE = "America/Santiago"


class User(BaseModel):
    id: str = Field(...)
    name: str = Field(...)
    calls: int = Field(...)
    last_call: datetime = Field(...)
    notifications: dict[int, Notification] = Field(default_factory=dict)

    def build_new_call(self) -> dict:
        """Builds the new call data"""
        return {"last_call": arrow.now(SANTIAGO_TIMEZONE).datetime, "calls": self.calls + 1, "name": self.name}
