import datetime
import logging
import pathlib
from typing import Callable, Union

from eventit_py.logging_backends import FileLoggingClient, MongoDBLoggingClient
from eventit_py.pydantic_events import BaseEvent

logger = logging.getLogger(__name__)

DEFAULT_LOG_FILEPATH = "eventit.log"


def _handle_timestamp(*args, **kwargs):
    """
    Returns the current timestamp in UTC timezone.

    Args:
        *args: Variable length argument list.
        **kwargs: Arbitrary keyword arguments.

    Returns:
        datetime.datetime: The current timestamp in UTC timezone.
    """
    return datetime.datetime.now(tz=datetime.timezone.utc)


def _return_function_name(func: Callable, *args, **kwargs) -> Union[str, None]:
    """
    Returns the name of the given function.

    Args:
        func (Callable): The function to get the name of.
        *args: Variable length argument list.
        **kwargs: Arbitrary keyword arguments.

    Returns:
        Union[str, None]: The name of the function as a string, or None if the function is None.

    """
    try:
        return func.__name__
    except AttributeError:
        if func is None:
            return None
        return str(func)


def _return_group(func: Callable, *args, **kwargs) -> Union[str, None]:
    """
    Returns the 'group' value from the 'context' dictionary if it exists, otherwise returns None.

    Args:
        func (Callable): The function to be called.
        *args: Variable length argument list.
        **kwargs: Arbitrary keyword arguments.

    Returns:
        Union[str, None]: The 'group' value from the 'context' dictionary if it exists, otherwise None.
    """
    if "context" in kwargs:
        context: dict = kwargs["context"]
        return context.get("group", None)
    return None


class BaseEventLogger:
    """
    Base class for event logging.

    This class provides a base implementation for event logging and serves as a template for subclasses to implement
    specific logging functionality.

    Args:
        default_event_type (Callable, optional): The default event type to be used if not provided. Defaults to None.
        ``**kwargs``: Additional keyword arguments for configuring the logger.

    Attributes:
        _default_event_type (Callable): The default event type.
        chosen_backend (str): The chosen backend for logging.
        db_client: The database client for logging.
        groups (list[str]): The list of event groups.
        _default_event_group (str): The default event group.
        builtin_metrics (dict[str, Callable]): The dictionary of built-in metrics.
        custom_metrics (dict[str, Callable]): The dictionary of custom metrics.

    """

    def __init__(self, default_event_type: Callable = None, **kwargs) -> None:
        self._default_event_type = default_event_type
        if default_event_type is None:
            self._default_event_type = BaseEvent
        self.chosen_backend = None
        self.db_client = None
        self.groups: list[str] = kwargs.get("groups", ["default"])
        self._default_event_group = kwargs.get("default_event_group", "default")
        self.groups.append(self._default_event_group)
        self.groups = list(set(self.groups))
        self.builtin_metrics: dict[str, Callable] = {
            "timestamp": _handle_timestamp,
            "function_name": _return_function_name,
            "group": _return_group,
        }

        self.custom_metrics: dict[str, Callable] = {}

        logger.debug("In BaseEventLogger Constructor")
        if "MONGO_URL" in kwargs:
            self.chosen_backend = "mongodb"
            mongo_url = kwargs.get("MONGO_URL")
            database_name = kwargs.get("database_name")
            self.db_client = MongoDBLoggingClient(
                mongo_url=mongo_url, database_name=database_name, groups=self.groups
            )

        # at end, default to using filepath if no other log specified
        if not self.chosen_backend or "directory" in kwargs:
            logger.debug("setting up filepath backend")
            self.chosen_backend = "filepath"
            directory = pathlib.Path(kwargs.get("directory", "./"))
            if not directory.exists():
                directory.mkdir(parents=True)
            self.db_client = FileLoggingClient(
                directory=kwargs.get("directory", "./"),
                groups=self.groups,
                separate_files=kwargs.get("separate_files", True),
                filename=kwargs.get("filename"),
            )

        logger.debug("BaseEventLogger configuration complete")

    def log_event(self):
        raise NotImplementedError(
            "log_event() wrapper unimplemented in BaseEventLogger"
        )

    def event(self):
        """Wrapper function to be implemented in subclass"""
        raise NotImplementedError("event() wrapper unimplemented in BaseEventLogger")
