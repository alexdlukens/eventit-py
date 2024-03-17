import pytest
from eventit_py.logging_backends import (
    FileLoggingClient,
    MongoDBLoggingClient,
)
from eventit_py.pydantic_events import BaseEvent


# define class derived from BaseEvent with two additional fields: field1 and field2
class MyEvent(BaseEvent):
    field1: str
    field2: int


def test_file_logging_client_search_events_by_query(tmp_path):
    groups = ["group1", "group2"]
    directory = tmp_path / "logs"
    client = FileLoggingClient(
        directory=directory,
        groups=groups,
        exclude_none=True,
    )
    query_dict = {"field1": "value1", "field2": 2}
    group = "group1"
    event_type = MyEvent
    limit = None

    # initial count of events by query should be 0
    assert client.count_events_by_query(query_dict, group, event_type) == 0
    assert client.count_events_by_query({}, group, event_type) == 0

    # Search events by query
    result = client.search_events_by_query(query_dict, group, event_type, limit)

    # Check that the result is an empty list
    assert result == []

    client.log_message(MyEvent(field1="value1", field2=2), group)

    result = client.search_events_by_query(query_dict, group, event_type, limit)
    assert len(result) == 1
    assert result[0].model_dump(include=["field1", "field2"]) == {
        "field1": "value1",
        "field2": 2,
    }

    # Add another event that should not match
    client.log_message(MyEvent(field1="value1", field2=3), group)

    # ensure that the new event was not matched
    result = client.search_events_by_query(query_dict, group, event_type, limit)
    assert len(result) == 1
    assert result[0].model_dump(include=["field1", "field2"]) == {
        "field1": "value1",
        "field2": 2,
    }

    # log several more events, and check that the limit parameter is working as expected
    for i in range(10):
        client.log_message(MyEvent(field1="value1", field2=2), group)
    result = client.search_events_by_query(query_dict, group, event_type, limit=5)
    assert len(result) == 5
    result = client.search_events_by_query(query_dict, group, event_type, limit=3)
    assert len(result) == 3
    result = client.search_events_by_query(query_dict, group, event_type, limit=0)

    event_search_direct_count = client.count_events_by_query(
        query_dict, group, event_type
    )
    assert len(result) == 11
    assert event_search_direct_count == 11


def test_file_logging_client_search_bad_query(tmp_path):
    groups = ["group1", "group2"]
    directory = tmp_path / "logs"
    client = FileLoggingClient(
        directory=directory,
        groups=groups,
        exclude_none=True,
    )

    query_dict = {"field3": "value1"}
    group = "group1"
    event_type = MyEvent
    limit = None

    # try to search for a field not present on MyEvent
    with pytest.raises(ValueError):
        client.search_events_by_query(query_dict, group, event_type, limit)

    # bad group
    with pytest.raises(ValueError):
        client.search_events_by_query({}, "group3", event_type, limit)


def test_mongodb_logging_client_search_events_by_query(get_mongo_uri):
    groups = ["group1", "group2"]
    client = MongoDBLoggingClient(
        mongo_url=get_mongo_uri,
        groups=groups,
        exclude_none=True,
    )
    query_dict = {"field1": "value1", "field2": 2}
    group = "group1"
    event_type = MyEvent
    limit = None

    # Search events by query
    result = client.search_events_by_query(query_dict, group, event_type, limit)

    # Check that the result is an empty list
    assert result == []

    assert client.count_events_by_query(query_dict, group, event_type) == 0
    assert client.count_events_by_query({}, group, event_type) == 0

    client.log_message(MyEvent(field1="value1", field2=2), group)

    result = client.search_events_by_query(query_dict, group, event_type, limit)
    assert len(result) == 1
    assert result[0].model_dump(include=["field1", "field2"]) == {
        "field1": "value1",
        "field2": 2,
    }

    # Add another event that should not match
    client.log_message(MyEvent(field1="value1", field2=3), group)

    # ensure that the new event was not matched
    result = client.search_events_by_query(query_dict, group, event_type, limit)
    assert len(result) == 1
    assert result[0].model_dump(include=["field1", "field2"]) == {
        "field1": "value1",
        "field2": 2,
    }

    # log several more events, and check that the limit parameter is working as expected
    for i in range(10):
        client.log_message(MyEvent(field1="value1", field2=2), group)
    result = client.search_events_by_query(query_dict, group, event_type, limit=5)
    assert len(result) == 5
    result = client.search_events_by_query(query_dict, group, event_type, limit=3)
    assert len(result) == 3
    result = client.search_events_by_query(query_dict, group, event_type, limit=0)

    event_search_direct_count = client.count_events_by_query(
        query_dict, group, event_type
    )

    assert len(result) == 11
    assert event_search_direct_count == 11


def test_mongodb_logging_client_search_bad_query(get_mongo_uri):
    groups = ["group1", "group2"]
    client = MongoDBLoggingClient(
        mongo_url=get_mongo_uri,
        groups=groups,
        exclude_none=True,
    )

    query_dict = {"field3": "value1"}
    group = "group1"
    event_type = MyEvent
    limit = None

    # try to search for a field not present on MyEvent
    with pytest.raises(ValueError):
        client.search_events_by_query(query_dict, group, event_type, limit)

    # bad group
    with pytest.raises(ValueError):
        client.search_events_by_query({}, "group3", event_type, limit)
