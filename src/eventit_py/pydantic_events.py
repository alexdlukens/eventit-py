import datetime
import logging
from typing import Optional

from pydantic import AwareDatetime, BaseModel, Field, field_validator

logger = logging.getLogger(__name__)


class BaseEvent(BaseModel):
    """Base class to be used for event tracking. Can be specialized for specific applications
    (Flask, Django, add custom data fields, etc)
    """

    user: Optional[str] = None
    group: Optional[str] = None
    function_name: Optional[str] = None
    description: Optional[str] = Field(strict=True, default=None)
    timestamp: AwareDatetime

    @field_validator("timestamp")
    def ensure_utc_timezone(cls, value: datetime.datetime):
        return value.astimezone(datetime.timezone.utc)

    def __repr__(self) -> str:
        return f"BaseEvent(timestamp={self.timestamp.isoformat()}, description={self.description})"

    def __str__(self) -> str:
        return str(self.model_dump_json())
