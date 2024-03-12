import io
import pathlib
import time
from datetime import datetime, timezone

import pytest
from eventit_py.logging_backends import (
    BaseLoggingClient,
    FileLoggingClient,
    MongoDBLoggingClient,
)
from eventit_py.pydantic_events import BaseEvent


def test_base_logging_client_init(tmp_path):
    groups = ["group1", "group2"]
    client = BaseLoggingClient(groups=groups, exclude_none=True)
    assert client._groups == groups
    assert client.exclude_none is True


def test_base_logging_client_log_message(tmp_path):
    groups = ["group1", "group2"]
    client = BaseLoggingClient(groups=groups, exclude_none=True)
    message = BaseEvent()
    group = "group1"
    with pytest.raises(NotImplementedError):
        client.log_message(message, group)


def test_base_logging_client_search_events_by_timestamp(tmp_path):
    groups = ["group1", "group2"]
    client = BaseLoggingClient(groups=groups, exclude_none=True)
    start_time = datetime(2022, 1, 1)
    end_time = datetime(2022, 1, 2)
    group = "group1"
    event_type = BaseEvent()
    limit = 10
    with pytest.raises(NotImplementedError):
        client.search_events_by_timestamp(
            start_time, end_time, group, event_type, limit
        )


def test_file_logging_client_init(tmp_path):
    groups = ["group1", "group2"]
    directory = tmp_path / "logs"
    filename = "log.txt"
    separate_files = True
    client = FileLoggingClient(
        directory=directory,
        groups=groups,
        filename=filename,
        exclude_none=True,
        separate_files=separate_files,
    )
    assert client._groups == groups
    assert client.exclude_none is True
    assert client._directory == directory.resolve()
    assert client._separate_files is True
    assert client._filename == filename
    assert isinstance(client.file_handles, dict)
    assert isinstance(client._filepaths, dict)
    assert len(client.file_handles) == len(groups)
    assert len(client._filepaths) == len(groups)
    assert all(isinstance(fh, io.TextIOBase) for fh in client.file_handles.values())
    assert all(isinstance(fp, pathlib.Path) for fp in client._filepaths.values())


def test_file_logging_client_init_single_file(tmp_path):
    groups = ["group1", "group2"]
    directory = tmp_path / "logs"
    filename = "log.txt"
    separate_files = False
    client = FileLoggingClient(
        directory=directory,
        groups=groups,
        filename=filename,
        exclude_none=True,
        separate_files=separate_files,
    )
    assert client._groups == groups
    assert client.exclude_none is True
    assert client._directory == directory.resolve()
    assert client._separate_files is False
    assert client._filename == filename
    assert isinstance(client.file_handles, dict)
    assert isinstance(client._filepaths, dict)
    assert len(client.file_handles) == len(groups)
    assert len(client._filepaths) == len(groups)
    assert all(isinstance(fh, io.TextIOBase) for fh in client.file_handles.values())
    assert all(isinstance(fp, pathlib.Path) for fp in client._filepaths.values())


def test_file_logging_client_log_message(tmp_path):
    groups = ["group1", "group2"]
    directory = tmp_path / "logs"
    client = FileLoggingClient(
        directory=directory,
        groups=groups,
        exclude_none=True,
    )
    message = BaseEvent()
    group = "group1"
    client.log_message(message, group)


def test_file_logging_client_log_message_invalid_group(tmp_path):
    groups = ["group1", "group2"]
    directory = tmp_path / "logs"
    client = FileLoggingClient(
        directory=directory,
        groups=groups,
        exclude_none=True,
    )
    message = BaseEvent()
    group = "invalid_group"
    with pytest.raises(ValueError):
        client.log_message(message, group)


def test_file_logging_client_search_events_by_timestamp(tmp_path):
    groups = ["group1", "group2"]
    directory = tmp_path / "logs"
    client = FileLoggingClient(
        directory=directory,
        groups=groups,
        exclude_none=True,
    )
    start_time = datetime(2022, 1, 1).astimezone(timezone.utc)
    end_time = datetime(2022, 1, 2).astimezone(timezone.utc)
    group = "group1"
    event_type = BaseEvent
    limit = 10
    events = client.search_events_by_timestamp(
        start_time, end_time, group, event_type, limit
    )

    assert len(events) == 0

    # log 10 blank events
    for _ in range(20):
        # Set end time to current time on the 5th iteration
        if _ == 4:
            end_time = datetime.now(tz=timezone.utc)
            time.sleep(0.05)
        message = BaseEvent()
        client.log_message(message, group)

    events = client.search_events_by_timestamp(
        start_time, end_time, group, event_type, limit
    )
    assert isinstance(events, list)
    assert all(isinstance(event, event_type) for event in events)
    assert len(events) == 4

    # ensure 10 logged events are now found by search (due to limit)
    end_time = datetime.now(tz=timezone.utc)
    events = client.search_events_by_timestamp(
        start_time, end_time, group, event_type, limit
    )
    assert isinstance(events, list)
    assert all(isinstance(event, event_type) for event in events)
    assert len(events) == 10

    # ensure all events are found with adequate limit for search
    end_time = datetime.now(tz=timezone.utc)
    events = client.search_events_by_timestamp(
        start_time, end_time, group, event_type, 20
    )
    assert isinstance(events, list)
    assert all(isinstance(event, event_type) for event in events)
    assert len(events) == 20


def test_mongodb_logging_client_search_events_by_timestamp(get_minikube_mongo_uri):
    groups = ["group1", "group2"]
    client = MongoDBLoggingClient(
        mongo_url=get_minikube_mongo_uri,
        groups=groups,
        exclude_none=True,
        database_name="eventit",
    )

    start_time = datetime(2022, 1, 1).astimezone(timezone.utc)
    end_time = datetime(2022, 1, 2).astimezone(timezone.utc)
    group = "group1"
    event_type = BaseEvent
    limit = 10
    events = client.search_events_by_timestamp(
        start_time, end_time, group, event_type, limit
    )

    assert len(events) == 0

    # log 10 blank events
    for _ in range(20):
        # Set end time to current time on the 5th iteration
        if _ == 4:
            end_time = datetime.now(tz=timezone.utc)
            time.sleep(0.05)

        message = BaseEvent()
        client.log_message(message, group)

    events = client.search_events_by_timestamp(
        start_time, end_time, group, event_type, limit
    )
    assert isinstance(events, list)
    assert all(isinstance(event, event_type) for event in events)
    assert len(events) == 4

    # ensure 10 logged events are now found by search (due to limit)
    end_time = datetime.now(tz=timezone.utc)
    events = client.search_events_by_timestamp(
        start_time, end_time, group, event_type, limit
    )
    assert isinstance(events, list)
    assert all(isinstance(event, event_type) for event in events)
    assert len(events) == 10

    # ensure all events are found with adequate limit for search
    end_time = datetime.now(tz=timezone.utc)
    events = client.search_events_by_timestamp(
        start_time, end_time, group, event_type, 20
    )
    assert isinstance(events, list)
    assert all(isinstance(event, event_type) for event in events)
    assert len(events) == 20
