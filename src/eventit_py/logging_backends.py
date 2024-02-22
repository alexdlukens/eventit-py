# This file will contain several different backends that can be used to interface with storage providers (e.g. MongoDB, filepath, etc.)

import io
import logging
import pathlib
from typing import TextIO

from pydantic import BaseModel

logger = logging.getLogger(__name__)

BACKEND_TYPES = ["mongodb", "filepath"]


class FileLoggingClient:
    """Append to files from provided filepath for logging"""

    def __init__(
        self,
        directory: str,
        groups: list[str],
        exclude_none: bool = True,
    ) -> None:
        logger.debug("Initializing FilepathDBClient")
        self._directory = pathlib.Path(directory).resolve()
        if not self._directory.is_dir():
            raise Exception(f"Provided path {directory} is not a directory")
        self._groups = groups
        self._filepaths: dict[str, pathlib.Path] = {
            group: self._directory.joinpath(f"{group}.log") for group in groups
        }
        self.file_handles: dict[str, TextIO] = {}
        for group in groups:
            self.file_handles[group] = open(
                self._filepaths[group], "a", encoding="utf-8"
            )
            logger.debug(
                "Opened %s file as backend for group %s", self._filepaths[group], group
            )

        self.exclude_none = exclude_none

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
        self, mongo_url: str, database_name: str, collection_name: str
    ) -> None:
        try:
            from pymongo import MongoClient
        except ImportError:
            logger.exception("Failed to import PyMongo, but MONGO_URL specified")
            raise
        self._mongo_url = mongo_url
        self._database_name = database_name
        self._collection_name = collection_name
        self.mongo_client = MongoClient(self._mongo_url)
        raise NotImplementedError()

    def log_message(self, message: BaseModel) -> None:
        """Log message into MongoDB. Message will be entered as a single document into configured collectoin

        Args:
            message (BaseModel): message to be logged

        Raises:
            NotImplementedError: _description_
        """
        raise NotImplementedError()
