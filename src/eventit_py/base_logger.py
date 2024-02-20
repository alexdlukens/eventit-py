import datetime
import logging
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


class BaseEventLogger:
    def __init__(self, default_event_type: Callable = None, **kwargs) -> None:
        self._default_event_type = default_event_type
        if default_event_type is None:
            self._default_event_type = BaseEvent
        self.chosen_backend = None
        self.db_client = None
        self.db_config = {}
        self.builtin_metrics = {
            "timestamp": _handle_timestamp,
            "function_name": _return_function_name,
        }

        logger.debug("In BaseEventLogger Constructor")
        if "MONGO_URL" in kwargs:
            self.chosen_backend = "mongodb"
            self.db_client = MongoDBLoggingClient()

        # at end, default to using filepath if no other log specified
        if not self.chosen_backend or "filepath" in kwargs:
            logger.debug("setting up filepath backend")
            self.chosen_backend = "filepath"
            self.db_client = FileLoggingClient(
                filepath=kwargs.get("filepath", DEFAULT_LOG_FILEPATH)
            )

        logger.debug("BaseEventLogger configuration complete")

    def log_event(self, **kwargs):
        raise NotImplementedError(
            "log_event() wrapper unimplemented in BaseEventLogger"
        )

    def event(self, **kwargs):
        """Wrapper function to be implemented in subclass"""
        raise NotImplementedError("event() wrapper unimplemented in BaseEventLogger")
