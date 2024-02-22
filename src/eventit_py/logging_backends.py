# This file will contain several different backends that can be used to interface with storage providers (e.g. MongoDB, filepath, etc.)

import io
import logging
import pathlib

from pydantic import BaseModel

logger = logging.getLogger(__name__)

BACKEND_TYPES = ["mongodb", "filepath"]


class FileLoggingClient:
    """Append to files from provided filepath for logging"""

    def __init__(self, filepath: str, exclude_none: bool = True) -> None:
        logger.debug("Initializing FilepathDBClient")
        self._filepath = pathlib.Path(filepath)
        self.file_handle = open(self._filepath, "a", encoding="utf-8")
        self.exclude_none = exclude_none

        logger.debug("Opened %s file as backend", self._filepath)

    def __del__(self):
        """Cleanup resources on destruction of object"""
        if not self.file_handle.closed:
            logger.debug("Closing handle to file %s", self._filepath)
            self.file_handle.close()

    def log_message(self, message: BaseModel) -> None:
        """Record the message provided into a single line, on the file opened
        Write newline to put next message on separate line (jsonlines format)
        Force file to be flushed to keep consistency for now

        Args:
            message (str): message to be logged
        """
        self.file_handle.seek(0, io.SEEK_END)
        self.file_handle.write(message.model_dump_json(exclude_none=self.exclude_none))
        self.file_handle.write("\n")
        self.file_handle.flush()


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
