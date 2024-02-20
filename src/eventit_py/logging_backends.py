# This file will contain several different backends that can be used to interface with storage providers (e.g. MongoDB, filepath, etc.)

import io
import logging
import pathlib

logger = logging.getLogger(__name__)

BACKEND_TYPES = ["mongodb", "filepath"]


class FileLoggingClient:
    def __init__(self, filepath: str) -> None:
        logger.debug("Initializing FilepathDBClient")
        self._filepath = pathlib.Path(filepath)
        self.file_handle = open(self._filepath, "a", encoding="utf-8")

        logger.debug("Opened %s file as backend", self._filepath)

    def __del__(self):
        # check if file is opened
        if not self.file_handle.closed:
            logger.debug("Closing handle to file %s", self._filepath)
            self.file_handle.close()

    def log_message(self, message: str) -> None:
        """Record the message provided into a single line, on the file opened
        Write newline to put next message on separate line (jsonlines format)
        Force file to be flushed to keep consistency for now
        Args:
            message (str): message to be logged
        """
        self.file_handle.seek(0, io.SEEK_END)
        self.file_handle.write(message)
        self.file_handle.write("\n")
        self.file_handle.flush()


class MongoDBLoggingClient:
    def __init__(self, mongo_url: str) -> None:
        try:
            from pymongo import MongoClient
        except ImportError:
            logger.exception("Failed to import PyMongo, but MONGO_URL specified")
            raise
        self._mongo_url = mongo_url
        self.mongo_client = MongoClient(self._mongo_url)
        raise NotImplementedError()

    def log_message(self, message: str) -> None:
        raise NotImplementedError()
