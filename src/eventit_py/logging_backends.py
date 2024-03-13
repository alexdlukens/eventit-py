# This file will contain several different backends that can be used to interface with storage providers (e.g. MongoDB, filepath, etc.)

import io
import logging
import pathlib
from datetime import datetime
from typing import List, TextIO

from eventit_py.pydantic_events import BaseEvent

logger = logging.getLogger(__name__)

BACKEND_TYPES = ["mongodb", "filepath"]
DEFAULT_DATABASE_NAME = "eventit"


class BaseLoggingClient:
    """
    Base class for logging clients.

    Args:
        groups (list[str]): A list of groups that the logging client belongs to.
        exclude_none (bool, optional): Whether to exclude None values when logging. Defaults to True.
    """

    def __init__(self, groups: list[str], exclude_none: bool = True) -> None:
        self._groups = groups
        self.exclude_none = exclude_none

    def log_message(self, message: BaseEvent, group: str) -> None:
        """
        Logs a message to the specified group.

        Args:
            message (BaseEvent): The message to be logged.
            group (str): The group to log the message to.

        Raises:
            NotImplementedError: This method must be implemented in derived classes.
        """
        raise NotImplementedError(
            "log_message method must be implemented in derived classes"
        )

    def search_events_by_timestamp(
        self,
        start_time: datetime,
        end_time: datetime,
        group: str,
        event_type: BaseEvent,
        limit: int = None,
    ) -> List[BaseEvent]:
        """
        Search events within a specified time range for a specific group and event type.

        Args:
            start_time (datetime): The start time of the search range.
            end_time (datetime): The end time of the search range.
            group (str): The group to search events in.
            event_type (str): The type of event to retrieve.
            limit (int, optional): The maximum number of events to return. Defaults to None.

        Returns:
            List[BaseModel]: A list of events that fall within the specified time range for the specified group and event type.
        """
        raise NotImplementedError(
            "search_events_by_timestamp method must be implemented in derived classes"
        )

    def search_events_by_query(
        self,
        query_dict: dict,
        group: str,
        event_type: BaseEvent,
        limit: int = None,
    ) -> List[BaseEvent]:
        """
        Search events based on a query dictionary for a specific group and event type.

        Args:
            query_dict (dict): A dictionary where the key is the field to match and the value is the value to match.
            group (str): The group to search events in.
            event_type (str): The type of event to retrieve.
            limit (int, optional): The maximum number of events to return. Defaults to None.

        Returns:
            List[BaseModel]: A list of events that match the query for the specified group and event type.
        """
        raise NotImplementedError(
            "search_events_by_query method must be implemented in derived classes"
        )


class FileLoggingClient(BaseLoggingClient):
    """Append to files from provided filepath for logging"""

    def __init__(
        self,
        directory: str,
        groups: list[str],
        filename: str = None,
        exclude_none: bool = True,
        separate_files: bool = True,
    ) -> None:
        super().__init__(groups, exclude_none)
        logger.debug("Initializing FilepathDBClient")
        self._directory = pathlib.Path(directory).resolve()
        if not self._directory.is_dir():
            self._directory.mkdir(parents=True, exist_ok=True)
            logger.debug("Created directory %s", self._directory)
        if not self._directory.is_dir():
            raise NotADirectoryError(f"Failed to create directory {self._directory}")

        self.file_handles: dict[str, TextIO] = {}
        self._filepaths: dict[str, pathlib.Path] = {}
        self._separate_files = separate_files
        self._filename = filename

        # setup logger for single or separate files
        if self._separate_files:
            self._setup_separate_files()
        else:
            self._setup_single_file()

    def _setup_separate_files(self):
        for group in self._groups:
            self._filepaths[group] = self._directory.joinpath(f"{group}.log")
            self.file_handles[group] = open(
                self._filepaths[group], "a", encoding="utf-8"
            )
            logger.debug(
                "Opened %s file as backend for group %s", self._filepaths[group], group
            )

    def _setup_single_file(self):
        single_filepath = self._directory.joinpath(self._filename)
        single_file_handle = open(single_filepath, "a", encoding="utf-8")
        for group in self._groups:
            self._filepaths[group] = single_filepath
            self.file_handles[group] = single_file_handle

    def __del__(self):
        """Cleanup resources on destruction of object"""
        for group, file_handle in self.file_handles.items():
            if not file_handle.closed:
                logger.debug("Closing handle to file %s", self._filepaths[group])
                file_handle.close()

    def log_message(self, message: BaseEvent, group: str) -> None:
        """Record the message provided into a single line, on the file opened
        Write newline to put next message on separate line (jsonlines format)
        Force file to be flushed to keep consistency for now

        Args:
            message (str): message to be logged
        """
        if group not in self._groups:
            raise ValueError(f"Invalid group {group} provided")
        self.file_handles[group].seek(0, io.SEEK_END)
        self.file_handles[group].write(
            message.model_dump_json(exclude_none=self.exclude_none)
        )
        self.file_handles[group].write("\n")
        self.file_handles[group].flush()

    def search_events_by_timestamp(
        self,
        start_time: datetime,
        end_time: datetime,
        group: str,
        event_type: BaseEvent,
        limit: int = None,
    ) -> List[BaseEvent]:
        """
        Search events within a specified time range for a specific group and event type.

        Args:
            start_time (datetime): The start time of the search range.
            end_time (datetime): The end time of the search range.
            group (str): The group to search events in.
            event_type (str): The type of event to retrieve.
            limit (int, optional): The maximum number of events to return. Defaults to None.

        Returns:
            List[BaseEvent]: A sorted list of events that fall within the specified time range for the specified group and event type.
        """

        if group not in self._groups:
            raise ValueError(f"Invalid group {group} provided")
        events = []
        # use new file handle to search whole file
        with open(self._filepaths[group], "r", encoding="utf-8") as file_handle:
            for line in file_handle:
                event = event_type.model_validate_json(line)
                if start_time <= event.timestamp <= end_time:
                    events.append(event)
                    if (limit is not None) and (len(events) >= limit):
                        break
        return sorted(events, key=lambda x: x.timestamp)

    def search_events_by_query(
        self, query_dict: dict, group: str, event_type: BaseEvent, limit: int = None
    ):
        """
        Search events based on a query dictionary for a specific group and event type.

        Args:
            query_dict (dict): A dictionary where the key is the field to match and the value is the value to match.
            group (str): The group to search events in.
            event_type (str): The type of event to retrieve.
            limit (int, optional): The maximum number of events to return. Defaults to None.

        Returns:
            List[BaseModel]: A list of events that match the query for the specified group and event type.
        """
        # if no limit, then we should set it to none for FileLoggingClient only
        if limit == 0:
            limit = None

        if group not in self._groups:
            raise ValueError(f"Invalid group {group} provided")
        # ensure all fields in query dict are in event_type class
        for key in query_dict.keys():
            if key not in event_type.model_fields:
                raise ValueError(f"Invalid key {key} in query_dict")

        events: List[BaseEvent] = []
        with open(self._filepaths[group], "r", encoding="utf-8") as file_handle:
            for line in file_handle:
                event = event_type.model_validate_json(line)
                try:
                    if all(
                        getattr(event, key) == value
                        for key, value in query_dict.items()
                    ):
                        events.append(event)
                        if limit is not None and len(events) >= limit:
                            return events
                except AttributeError:
                    logger.exception("Failed to match query_dict to event")
                    continue
        return sorted(events, key=lambda x: x.timestamp)


class MongoDBLoggingClient(BaseLoggingClient):
    """
    Utilize MongoDB as a backend for storing log information.

    This class provides a logging client that uses MongoDB as the backend for storing log information.
    It inherits from the `BaseLoggingClient` class.

    Attributes:
        mongo_url (str): The URL of the MongoDB server.
        groups (list[str]): A list of log groups to be used.
        exclude_none (bool, optional): Whether to exclude None values when logging. Defaults to True.
        database_name (str, optional): The name of the MongoDB database to use. If not provided, a default name will be used.

    Methods:
        __init__: Initializes the MongoDBLoggingClient instance.
        reset_db: Resets the database by dropping the current database from MongoDB.
        log_message: Logs a message into MongoDB.
        search_events_by_timestamp: Search events within a specified time range for a specific group and event type.

    """

    def __init__(
        self,
        mongo_url: str,
        groups: list[str],
        exclude_none: bool = True,
        database_name: str = None,
    ) -> None:
        super().__init__(groups, exclude_none)
        logger.debug("Initializing MongoDBLoggingClient")
        try:
            from bson.codec_options import CodecOptions
            from pymongo import MongoClient
            from pymongo.errors import ServerSelectionTimeoutError
        except ImportError:
            logger.exception(
                "Failed to import from PyMongo in MongoDBLoggingClient constructor"
            )
            raise
        self._mongo_url = mongo_url
        self._database_name = database_name
        if self._database_name is None:
            self._database_name = DEFAULT_DATABASE_NAME

        self._mongo_client = MongoClient(self._mongo_url)
        try:
            self._mongo_client.list_database_names()
        except ServerSelectionTimeoutError:
            print("Failed to connect to MongoDB")
            raise
        logger.debug("Initial MongoDB connection successful")
        self.reset_db()
        self._db = self._mongo_client[self._database_name].with_options(
            CodecOptions(tz_aware=True)
        )

    def reset_db(self):
        """
        Resets the database by dropping the current database from MongoDB.

        This method drops the database specified by the `_database_name` attribute from MongoDB.
        It is important to note that this action is irreversible and will permanently delete all data in the database.

        Args:
            None

        Returns:
            None
        """
        logger.debug("About to drop database %s from MongoDB", self._database_name)
        self._mongo_client.drop_database(self._database_name)

    def log_message(self, message: BaseEvent, group: str) -> None:
        """
        Log a message into MongoDB.

        This method logs a message into MongoDB by inserting it as a single document into the configured collection.

        Args:
            message (BaseEvent): The message to be logged.
            group (str): The log group to which the message belongs.

        Raises:
            ValueError: If an invalid log group is provided.

        Returns:
            None
        """
        if group not in self._groups:
            raise ValueError(f"Invalid group {group} provided")
        self._db[group].insert_one(message.model_dump(exclude_none=self.exclude_none))

    def search_events_by_timestamp(
        self,
        start_time: datetime,
        end_time: datetime,
        group: str,
        event_type: BaseEvent,
        limit: int = None,
    ) -> List[BaseEvent]:
        """
        Search events within a specified time range for a specific group and event type.

        Args:
            start_time (datetime): The start time of the search range.
            end_time (datetime): The end time of the search range.
            group (str): The group to search events in.
            event_type (str): The type of event to retrieve.
            limit (int, optional): The maximum number of events to return. Defaults to None.

        Returns:
            List[BaseEvent]: A sorted list of events that fall within the specified time range for the specified group and event type.
        """
        if group not in self._groups:
            raise ValueError(f"Invalid group {group} provided")
        query = {"timestamp": {"$gte": start_time, "$lte": end_time}}
        events = self._db[group].find(query).limit(limit if limit else 0)
        events = [event_type.model_validate(event) for event in events]
        return sorted(events, key=lambda x: x.timestamp)

    def search_events_by_query(
        self, query_dict: dict, group: str, event_type: BaseEvent, limit: int = None
    ):
        """
        Search events based on a query dictionary for a specific group and event type.

        Args:
            query_dict (dict): A dictionary where the key is the field to match and the value is the value to match.
            group (str): The group to search events in.
            event_type (str): The type of event to retrieve.
            limit (int, optional): The maximum number of events to return. Defaults to None.

        Returns:
            List[BaseModel]: A list of events that match the query for the specified group and event type.
        """
        if group not in self._groups:
            raise ValueError(f"Invalid group {group} provided")

        # ensure all fields in query dict are in event_type class
        for key in query_dict.keys():
            if key not in event_type.model_fields:
                raise ValueError(f"Invalid key {key} in query_dict")

        cursor = self._db[group].find(query_dict).limit(limit if limit else 0)
        events: List[BaseEvent] = [event_type(**doc) for doc in cursor]
        return sorted(events, key=lambda x: x.timestamp)
