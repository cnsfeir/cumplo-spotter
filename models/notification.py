# pylint: disable=no-member

import os
from datetime import datetime

import arrow
from dotenv import load_dotenv
from pydantic import BaseModel, Field

load_dotenv()

EXPIRACY = int(os.getenv("EXPIRACY", "2"))
SANTIAGO_TIMEZONE = "America/Santiago"


class Notification(BaseModel):
    id: int = Field(...)
    date: datetime = Field(...)

    @property
    def has_expired(self) -> bool:
        """
        Checks if the notification has expired
        """
        return arrow.get(self.date).shift(hours=EXPIRACY) < arrow.now(SANTIAGO_TIMEZONE)
