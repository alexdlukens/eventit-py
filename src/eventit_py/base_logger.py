import datetime
import logging
import pathlib
from typing import Callable, Union

from eventit_py.logging_backends import FileLoggingClient, MongoDBLoggingClient
from eventit_py.pydantic_events import BaseEvent

logger = logging.getLogger(__name__)

DEFAULT_LOG_FILEPATH = "eventit.log"


def _handle_timestamp(*args, **kwargs):
    return datetime.datetime.now()


def _return_function_name(func: Callable, *args, **kwargs) -> Union[str, None]:
    try:
        return func.__name__
    except AttributeError:
        if func is None:
            return None
        return str(func)


def _return_group(func: Callable, *args, **kwargs) -> Union[str, None]:
    if "context" in kwargs:
        context: dict = kwargs["context"]
        return context.get("group", None)
    return None


class BaseEventLogger:
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
