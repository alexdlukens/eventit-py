# This file will contain several different backends that can be used to interface with storage providers (e.g. MongoDB, filepath, etc.)

import io
import logging
import pathlib
from typing import TextIO

from pydantic import BaseModel

logger = logging.getLogger(__name__)

BACKEND_TYPES = ["mongodb", "filepath"]
DEFAULT_DATABASE_NAME = "eventit"


class FileLoggingClient:
    """Append to files from provided filepath for logging"""

    def __init__(
        self,
        directory: str,
        groups: list[str],
        filename: str = None,
        exclude_none: bool = True,
        separate_files: bool = True,
    ) -> None:
        logger.debug("Initializing FilepathDBClient")
        self._directory = pathlib.Path(directory).resolve()
        if not self._directory.is_dir():
            raise NotADirectoryError(f"Provided path {directory} is not a directory")
        self._groups = groups

        self.file_handles: dict[str, TextIO] = {}
        self._filepaths: dict[str, pathlib.Path] = {}
        self._separate_files = separate_files
        self._filename = filename

        # setup logger for single or separate files
        if self._separate_files:
            self._setup_separate_files()
        else:
            self._setup_single_file()

        self.exclude_none = exclude_none

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

    def log_message(self, message: BaseModel, group: str) -> None:
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


class MongoDBLoggingClient:
    """Utilize MongoDB as a backend for storing log information"""

    def __init__(
        self,
        mongo_url: str,
        groups: list[str],
        exclude_none: bool = True,
        database_name: str = None,
    ) -> None:
        logger.debug("Initializing MongoDBLoggingClient")
        try:
            from pymongo import MongoClient
            from pymongo.errors import ServerSelectionTimeoutError
        except ImportError:
            logger.exception(
                "Failed to import from PyMongo in MongoDBLoggingClient constructor"
            )
            raise
        self._mongo_url = mongo_url
        self._groups = groups
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
        self._db = self._mongo_client[self._database_name]
        self.exclude_none = exclude_none

    def reset_db(self):
        logger.debug("About to drop database %s from MongoDB", self._database_name)
        self._mongo_client.drop_database(self._database_name)

    def log_message(self, message: BaseModel, group: str) -> None:
        """Log message into MongoDB. Message will be entered as a single document into configured collectoin

        Args:
            message (BaseModel): message to be logged

        Raises:
            NotImplementedError: _description_
        """
        if group not in self._groups:
            raise ValueError(f"Invalid group {group} provided")
        self._db[group].insert_one(
            message.model_dump(mode="json", exclude_none=self.exclude_none)
        )
