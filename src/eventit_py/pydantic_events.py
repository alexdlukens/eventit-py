import datetime
import logging
import uuid
from typing import Optional

from pydantic import (
    UUID4,
    AwareDatetime,
    BaseModel,
    Field,
    field_serializer,
    field_validator,
)

logger = logging.getLogger(__name__)


class BaseEvent(BaseModel):
    """
    Base class to be used for event tracking. Can be specialized for specific applications
    (Flask, Django, add custom data fields, etc)

    Args:
        user (Optional[str]): The user associated with the event.
        group (Optional[str]): The group associated with the event.
        function_name (Optional[str]): The name of the function associated with the event.
        event_location (Optional[str]): The location of the event.
        description (Optional[str]): The description of the event.
        uuid (UUID4): The UUID of the event.
        timestamp (AwareDatetime): The timestamp of the event in UTC timezone.

    Functions:
        ensure_utc_timezone(value: datetime.datetime): A field validator method to ensure the timestamp is in UTC timezone.
        serialize_uuid(value: UUID4, _info): A field serializer method to serialize the UUID value.
        __repr__(): Returns a string representation of the BaseEvent object.
        __str__(): Returns a string representation of the BaseEvent object using the model_dump_json() method.
    """

    user: Optional[str] = None
    group: Optional[str] = None
    function_name: Optional[str] = None
    event_location: Optional[str] = None
    description: Optional[str] = Field(strict=True, default=None)
    uuid: UUID4 = Field(default_factory=uuid.uuid4)
    timestamp: AwareDatetime = Field(
        default_factory=lambda: datetime.datetime.now(datetime.timezone.utc)
    )

    @field_validator("timestamp")
    def ensure_utc_timezone(cls, value: datetime.datetime):
        return value.astimezone(datetime.timezone.utc)

    @field_serializer("uuid")
    def serialize_uuid(self, value: UUID4, _info):
        return str(value)

    def __repr__(self) -> str:  # pragma: no cover
        return f"BaseEvent(timestamp={self.timestamp.isoformat()}, description={self.description})"

    def __str__(self) -> str:  # pragma: no cover
        return str(self.model_dump_json())
