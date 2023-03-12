# pylint: disable=no-member

from datetime import datetime

import arrow
from dotenv import load_dotenv
from pydantic import BaseModel, Field

load_dotenv()

SANTIAGO_TIMEZONE = "America/Santiago"


class Notification(BaseModel):
    id: int = Field(...)
    date: datetime = Field(...)

    def has_expired(self, expiracy_hours: int) -> bool:
        """
        Checks if the notification has expired
        """
        return arrow.get(self.date).shift(hours=expiracy_hours) < arrow.now(SANTIAGO_TIMEZONE)
