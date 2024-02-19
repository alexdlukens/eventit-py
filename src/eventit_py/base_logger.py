import datetime
import json
import logging
from typing import Callable

logger = logging.getLogger(__name__)

BACKEND_TYPES = ["mongodb", "filepath"]
DEFAULT_LOG_FILEPATH = "eventit.log"


def _handle_timestamp(*args, **kwargs):
    return datetime.datetime.now()


def _return_function_name(func: Callable, *args, **kwargs):
    return func.__name__


class BaseEventLogger:
    def __init__(self, **kwargs) -> None:
        self.chosen_backend = None
        self.db_client = None
        self.db_config = {}
        self.builtin_metrics = {
            "timestamp": _handle_timestamp,
            "function_name": _return_function_name,
        }

        logger.debug("In BaseEventLogger Constructor")
        if "MONGO_URL" in kwargs:
            try:
                from pymongo import MongoClient
            except ImportError:
                logger.exception("Failed to import PyMongo, but MONGO_URL specified")
                raise

            self.chosen_backend = "mongodb"
            self.db_client = MongoClient()

        # raise TypeError(
        # "Attempting to Instantiate BaseAuthitPlugin directly. Use a specific plugin instead"
        # )

        # at end, default to using filepath if no other log specified
        if not self.chosen_backend or "filepath" in kwargs:
            logger.debug("setting up filepath backend")
            self.chosen_backend = "filepath"
            self.filepath = kwargs.get("filepath", DEFAULT_LOG_FILEPATH)
            self.db_client = open(self.filepath, "a", encoding="utf-8")
            logger.debug("Opened %s file as backend", self.filepath)

        logger.debug("BaseEventLogger configuration complete")

    def __del__(self):
        if self.chosen_backend == "filepath":
            self.db_client.close()

    def _log_metric(self, info):
        if self.chosen_backend == "mongodb":
            # log to mongo
            pass
        elif self.chosen_backend == "filepath":
            json.dump(info, self.db_client)

        return

    def track_metrics(self, func):
        """General wrapper used to track metrics for a specific API route

        Args:
            func (Callable): Function to be wrapped
        """

        raise NotImplementedError("track_metrics unimplemented in BaseAuthitPlugin")

        def wrapper():
            # log X info beforehand
            self._log_metric({"hello": "world"})
            func()
            # log Y info afterward

        return wrapper
