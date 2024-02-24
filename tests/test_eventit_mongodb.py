import datetime
from unittest.mock import ANY

import pytest
from eventit_py.event_logger import EventLogger
from eventit_py.logging_backends import MongoDBLoggingClient
from eventit_py.pydantic_events import DEFAULT_TIMESTAMP_FORMAT
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError

MONGO_URL = "mongodb://root:e6OGc80Oux@127.0.0.1:27017/?authSource=admin"
EVENTIT_DB_NAME = "eventit"


@pytest.mark.mongodb
def test_event_logger_setup():
    mongo_client = MongoClient(MONGO_URL)
    try:
        mongo_client.list_database_names()
    except ServerSelectionTimeoutError:
        print("Failed to connect to MongoDB")
        raise
    try:
        eventit = EventLogger(MONGO_URL=MONGO_URL, database=EVENTIT_DB_NAME)

        assert isinstance(eventit.db_client, MongoDBLoggingClient)

    except Exception:
        pytest.fail("failed to initialize MongoDBLoggingClient")
    # finally:
    #     mongo_client.drop_database(EVENTIT_DB_NAME)


@pytest.mark.mongodb
def test_event_logger_single_event():
    mongo_client = MongoClient(MONGO_URL)
    try:
        mongo_client.list_database_names()
    except ServerSelectionTimeoutError:
        print("Failed to connect to MongoDB")
        raise
    eventit = EventLogger(MONGO_URL=MONGO_URL, database=EVENTIT_DB_NAME)

    @eventit.event(description="This is a basic test for MongoDB")
    def this_is_a_mongodb_test():
        return -1

    timestamp_before = datetime.datetime.now(tz=datetime.timezone.utc)
    this_is_a_mongodb_test()
    timestamp_after = datetime.datetime.now(tz=datetime.timezone.utc)
    first_record = mongo_client[EVENTIT_DB_NAME]["default"].find_one(
        {
            "timestamp": {
                "$gte": timestamp_before.strftime(DEFAULT_TIMESTAMP_FORMAT),
                "$lte": timestamp_after.strftime(DEFAULT_TIMESTAMP_FORMAT),
            }
        },
        {"_id": 0},
    )

    assert first_record == {
        "timestamp": ANY,
        "group": "default",
        "description": "This is a basic test for MongoDB",
        "function_name": "this_is_a_mongodb_test",
    }
    # finally:
    #     mongo_client.drop_database(EVENTIT_DB_NAME)
