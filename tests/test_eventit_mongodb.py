import datetime
import time

import pytest
from bson.codec_options import CodecOptions
from eventit_py.event_logger import EventLogger
from eventit_py.logging_backends import MongoDBLoggingClient
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError

# MONGO_URL = "mongodb://root:e6OGc80Oux@127.0.0.1:27017/?authSource=admin"
EVENTIT_DB_NAME = "eventit"


@pytest.mark.mongodb
def test_mongodb_logger_setup(get_mongo_uri):
    mongo_client = MongoClient(get_mongo_uri)
    try:
        mongo_client.list_database_names()
    except ServerSelectionTimeoutError:
        print("Failed to connect to MongoDB")
        raise
    try:
        eventit = EventLogger(MONGO_URL=get_mongo_uri, database=EVENTIT_DB_NAME)

        assert isinstance(eventit.db_client, MongoDBLoggingClient)

    except Exception:
        pytest.fail("failed to initialize MongoDBLoggingClient")


@pytest.mark.mongodb
def test_mongodb_many_events(get_mongo_uri):
    mongo_client = MongoClient(get_mongo_uri)

    eventit = EventLogger(MONGO_URL=get_mongo_uri, database=EVENTIT_DB_NAME)

    @eventit.event(description="This is a basic test for MongoDB")
    def this_is_a_mongodb_test():
        return -1

    timestamps: list[datetime.datetime] = []
    timestamps.append(datetime.datetime.now(tz=datetime.timezone.utc))
    time.sleep(0.001)
    # enter 1000 records, keeping track of after timestamps
    for _ in range(1000):
        this_is_a_mongodb_test()
        time.sleep(0.001)
        timestamps.append(datetime.datetime.now(tz=datetime.timezone.utc))

    for i in range(len(timestamps) - 1):
        print(f"{i=}")
        assert (
            mongo_client[EVENTIT_DB_NAME]["default"]
            .with_options(CodecOptions(tz_aware=True))
            .count_documents(
                {
                    "timestamp": {
                        "$gte": timestamps[i],
                        "$lt": timestamps[i + 1],
                    }
                },
            )
            == 1
        )
