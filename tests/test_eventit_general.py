import datetime
import json
import os
import shutil
import time
from unittest.mock import ANY

from eventit_py.event_logger import EventLogger
from eventit_py.pydantic_events import BaseEvent

# cur_path = pathlib.Path(__file__)
# sys.path.insert(0, cur_path.parent.parent)


def test_event_logger_setup(tmp_path):
    tmp_file = tmp_path / "default.log"
    if tmp_path.exists():
        shutil.rmtree(tmp_path, ignore_errors=True)

    try:
        eventit = EventLogger(directory=str(tmp_path))

        assert eventit.db_client._filepaths == {
            "default": (tmp_path / "default.log").resolve()
        }
        assert tmp_file.exists()

    finally:
        shutil.rmtree(tmp_path, ignore_errors=True)


def test_event_logger_single_event(tmp_path):
    tmp_file = tmp_path / "default.log"
    start_time = datetime.datetime.now(tz=datetime.timezone.utc)
    if tmp_path.exists():
        shutil.rmtree(tmp_path, ignore_errors=True)

    try:
        eventit = EventLogger(directory=str(tmp_path))

        @eventit.event(tracking_details={"timestamp": True})
        def this_is_a_test():
            return "Hello, World"

        print(this_is_a_test())
        time.sleep(0.1)
        end_time = datetime.datetime.now(tz=datetime.timezone.utc)
        with open(tmp_file, "r", encoding="utf-8") as f:
            assert len(lines := f.readlines()) == 1
            first_line = json.loads(lines[0])
            assert first_line == {
                "timestamp": ANY,
                "uuid": ANY,
            }

            loaded_event = BaseEvent.model_validate(first_line)
            assert loaded_event.timestamp > start_time
            assert loaded_event.timestamp < end_time

    finally:
        shutil.rmtree(tmp_path, ignore_errors=True)


def test_event_function_name(tmp_path):
    tmp_file = tmp_path / "default.log"
    if tmp_path.exists():
        shutil.rmtree(tmp_path, ignore_errors=True)

    try:
        eventit = EventLogger(directory=tmp_path)

        @eventit.event(tracking_details={"timestamp": True, "function_name": True})
        def this_is_a_test():
            return "Hello, World"

        print(this_is_a_test())

        with open(tmp_file, "r", encoding="utf-8") as f:
            assert len(lines := f.readlines()) == 1
            first_line = json.loads(lines[0])
            assert first_line == {
                "timestamp": ANY,
                "uuid": ANY,
                "function_name": "this_is_a_test",
            }

    finally:
        shutil.rmtree(tmp_path, ignore_errors=True)


def test_log_separate_event_default(tmp_path):
    tmp_file = tmp_path / "default.log"
    if tmp_path.exists():
        shutil.rmtree(tmp_path, ignore_errors=True)

    try:
        eventit = EventLogger(filepath=str(tmp_file), directory=tmp_path)

        # log event with specific name
        eventit.log_event("Banana")

        with open(tmp_file, "r", encoding="utf-8") as f:
            assert len(lines := f.readlines()) == 1
            first_line = json.loads(lines[0])
            assert first_line == {
                "timestamp": ANY,
                "uuid": ANY,
                "event_location": "test_eventit_general:test_log_separate_event_default",
                "group": "default",
                "function_name": "Banana",
            }

        # log empty event with just timestamp
        eventit.log_event()

        with open(tmp_file, "r", encoding="utf-8") as f:
            assert len(lines := f.readlines()) == 2
            first_line = json.loads(lines[0])
            second_line = json.loads(lines[1])
            assert first_line == {
                "timestamp": ANY,
                "uuid": ANY,
                "event_location": "test_eventit_general:test_log_separate_event_default",
                "group": "default",
                "function_name": "Banana",
            }
            assert second_line == {
                "timestamp": ANY,
                "uuid": ANY,
                "event_location": "test_eventit_general:test_log_separate_event_default",
                "group": "default",
            }

    finally:
        shutil.rmtree(tmp_path, ignore_errors=True)


def test_setup_custom_group(tmp_path):
    """Test basic funcitonality for separate groups.
    I want to be able to toggle whether group is shown in tracking details (default to True),
    log separate "groups" to separate files, and specify which group each event is logged as
    in the event decorator"""
    if tmp_path.exists():
        shutil.rmtree(tmp_path, ignore_errors=True)
    tmp_file = tmp_path / "custom1.log"
    if tmp_file.exists():
        os.remove(tmp_file)

    try:
        eventit = EventLogger(
            directory=tmp_path, groups=["default", "custom1"], separate_files=True
        )

        @eventit.event(
            group="custom1",
            tracking_details={"timestamp": True, "function_name": True, "group": False},
        )
        def this_is_a_test():
            return "Hello, World"

        print(this_is_a_test())

        with open(tmp_file, "r", encoding="utf-8") as f:
            assert len(lines := f.readlines()) == 1
            first_line = json.loads(lines[0])
            assert first_line == {
                "timestamp": ANY,
                "uuid": ANY,
                "function_name": "this_is_a_test",
            }

    finally:
        shutil.rmtree(tmp_path, ignore_errors=True)


def test_setup_custom_group_single_file(tmp_path):
    """Logging different groups to single file should append to list, not overwriting any other entries"""
    if tmp_path.exists():
        shutil.rmtree(tmp_path, ignore_errors=True)
    tmp_file = tmp_path / "eventit.log"

    try:
        eventit = EventLogger(
            directory=tmp_path,
            filename="eventit.log",
            groups=["default", "custom1"],
            separate_files=False,
        )

        @eventit.event(
            group="custom1",
            tracking_details={"timestamp": True, "function_name": True, "group": True},
        )
        def this_is_a_test():
            return "Hello, World"

        @eventit.event(
            group="default",
            tracking_details={"timestamp": True, "function_name": True, "group": True},
        )
        def this_is_a_test2():
            return "Hello, World2"

        print(this_is_a_test())

        print(this_is_a_test2())

        with open(tmp_file, "r", encoding="utf-8") as f:
            assert len(lines := f.readlines()) == 2
            first_line = json.loads(lines[0])
            assert first_line == {
                "timestamp": ANY,
                "uuid": ANY,
                "function_name": "this_is_a_test",
                "group": "custom1",
            }
            second_line = json.loads(lines[1])
            assert second_line == {
                "timestamp": ANY,
                "uuid": ANY,
                "function_name": "this_is_a_test2",
                "group": "default",
            }

    finally:
        shutil.rmtree(tmp_path, ignore_errors=True)


def test_multiple_groups_single_file(tmp_path):
    """Test basic funcitonality for separate groups.
    I want to be able to toggle whether group is shown in tracking details (default to True),
    log separate "groups" to separate files, and specify which group each event is logged as
    in the event decorator"""
    if tmp_path.exists():
        shutil.rmtree(tmp_path, ignore_errors=True)
    tmp_file = tmp_path / "eventit.log"

    try:
        eventit = EventLogger(
            directory=tmp_path,
            filename="eventit.log",
            groups=["default", "custom1"],
            separate_files=False,
        )

        @eventit.event(
            group="custom1",
            tracking_details={"timestamp": True, "function_name": True, "group": True},
        )
        def this_is_a_test():
            return "Hello, World"

        print(this_is_a_test())

        with open(tmp_file, "r", encoding="utf-8") as f:
            assert len(lines := f.readlines()) == 1
            first_line = json.loads(lines[0])
            assert first_line == {
                "timestamp": ANY,
                "uuid": ANY,
                "function_name": "this_is_a_test",
                "group": "custom1",
            }

    finally:
        shutil.rmtree(tmp_path, ignore_errors=True)
