import datetime
import logging
import uuid
from typing import Optional

from pydantic import (
    UUID4,
    AwareDatetime,
    BaseModel,
    Field,
    field_validator,
)

logger = logging.getLogger(__name__)


def _handle_timestamp(*args, **kwargs):
    """
    Returns the current timestamp in UTC timezone.

    Args:
        *args: Variable length argument list.
        **kwargs: Arbitrary keyword arguments.

    Returns:
        datetime.datetime: The current timestamp in UTC timezone.
    """
    value = datetime.datetime.now(tz=datetime.timezone.utc)
    return value.replace(microsecond=int(value.microsecond / 1000) * 1000)


def _subtract_time_delta(
    time_obj: datetime.datetime, delta: datetime.timedelta
) -> tuple[datetime.datetime, datetime.timedelta]:
    seconds = int(time_obj.timestamp())
    remainder = datetime.timedelta(
        seconds=seconds % delta.total_seconds(),
        microseconds=time_obj.microsecond,
    )
    quotient = time_obj - remainder
    return quotient, remainder


class BaseEvent(BaseModel):
    """
    Base class to be used for event tracking. Can be specialized for specific applications
    (Flask, Django, add custom data fields, etc)

    Timestamp and UUID fields are always present, and automatically generated

    Args:
        user (Optional[str]): The user associated with the event.
        group (Optional[str]): The group associated with the event.
        function_name (Optional[str]): The name of the function associated with the event.
        event_location (Optional[str]): The location of the event.
        description (Optional[str]): The description of the event.
        uuid (UUID4): The UUID of the event.
        timestamp (AwareDatetime): The timestamp of the event in UTC timezone. Uses millisecond accuracy

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
    timestamp: AwareDatetime = Field(default_factory=_handle_timestamp)

    @field_validator("timestamp")
    @classmethod
    def ensure_utc_timezone(cls, value: datetime.datetime):
        return value.astimezone(datetime.timezone.utc).replace(
            microsecond=int(value.microsecond / 1000) * 1000
        )

    def __repr__(self) -> str:  # pragma: no cover
        return f"BaseEvent(timestamp={self.timestamp.isoformat()}, description={self.description})"

    def __str__(self) -> str:  # pragma: no cover
        return str(self.model_dump_json())


class BaseCountableEvent(BaseEvent):
    """
    Represents a countable event with a time window and number of events.

    Attributes:
        time_window (int): Time window in seconds.
        count (int): Number of events in the time window.
    """

    time_window: int = Field(default=15, description="Time window in seconds")
    count: int = Field(default=1, description="Number of events in the time window")

    @field_validator("time_window")  # ensure that the time window is greater than 0
    @classmethod
    def validate_time_window(cls, value: float):
        if value <= 0:
            raise ValueError("Time window must be greater than 0")
        return value
