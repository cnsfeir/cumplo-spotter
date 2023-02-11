# pylint: disable=no-member

from pydantic import BaseModel, Field


class Configuration(BaseModel):
    filter_notified: bool = Field(True)
