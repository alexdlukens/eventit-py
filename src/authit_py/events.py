import datetime
import logging
from typing import Any

DEFAULT_TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S %Z"

logger = logging.getLogger(__name__)


class BaseEvent:
    """Base class to be used for event tracking. Can be specialized for specific applications
    (Flask, Django, add custom data fields, etc)
    """

    def __init__(
        self,
        timestamp: str = None,
        user: str = None,
        group: str = None,
        route: str = None,
    ) -> None:
        self.timestamp: datetime.datetime = None
        if timestamp is None:
            self.timestamp = datetime.datetime.now(tz=datetime.timezone.utc)
        else:
            self.timestamp = datetime.datetime.strptime(
                timestamp, DEFAULT_TIMESTAMP_FORMAT
            )
            self.timestamp = self.timestamp.astimezone(datetime.timezone.utc)

        self.user = user
        self.group = group
        self.route = route

        pass

    def __repr__(self) -> str:
        return f"BaseEvent(timestamp={self.timestamp.strftime(DEFAULT_TIMESTAMP_FORMAT)}, user={self.user}, group={self.group}, route={self.route})"

    def __str__(self) -> str:
        return str(self.toJSON())

    def toJSON(self) -> dict[str, Any]:
        """Convert BaseEvent into a format able to be stored in DB (a dictionary, for now)

        Returns:
            dict: dictionary representation of event
        """
        return {
            "timestamp": self.timestamp.strftime(DEFAULT_TIMESTAMP_FORMAT),
            "user": self.user,
            "group": self.group,
            "route": self.route,
        }
