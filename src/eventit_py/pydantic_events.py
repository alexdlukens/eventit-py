import datetime
import logging
from typing import Optional

from pydantic import BaseModel, field_serializer, field_validator

DEFAULT_TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S %Z"

logger = logging.getLogger(__name__)


class BaseEvent(BaseModel):
    """Base class to be used for event tracking. Can be specialized for specific applications
    (Flask, Django, add custom data fields, etc)
    """

    user: Optional[str] = None
    group: Optional[str] = None
    timestamp: datetime.datetime

    @field_validator("timestamp")
    def ensure_utc_timezone(cls, value: datetime.datetime):
        utc_offset = value.utcoffset()
        if utc_offset is not None:
            value = value.astimezone(datetime.timezone.utc)
        return value

    @field_serializer("timestamp")
    def timestamp_serializer(self, timestamp: datetime.datetime, _info):
        return timestamp.strftime(DEFAULT_TIMESTAMP_FORMAT)

    def __repr__(self) -> str:
        return f"BaseEvent(timestamp={self.timestamp.strftime(DEFAULT_TIMESTAMP_FORMAT)}, user={self.user}, group={self.group}, route={self.route})"

    def __str__(self) -> str:
        return str(self.model_dump_json())
