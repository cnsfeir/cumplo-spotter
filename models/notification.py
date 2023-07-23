# pylint: disable=no-member

from datetime import datetime

import arrow
from pydantic import BaseModel, Field


class Notification(BaseModel):
    id: int = Field(...)
    date: datetime = Field(...)

    def has_expired(self, expiration_minutes: int) -> bool:
        """Checks if the notification has expired"""
        return arrow.get(self.date).shift(minutes=expiration_minutes) < arrow.utcnow()
