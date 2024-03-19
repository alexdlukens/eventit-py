import json
import os
import shutil
import time
from unittest.mock import ANY

from eventit_py.event_logger import EventLogger
from eventit_py.pydantic_events import BaseEvent

five = 5


def test_setup_custom_metric(tmp_path):
    """Test basic funcitonality for custom metrics"""
    if tmp_path.exists():
        shutil.rmtree(tmp_path, ignore_errors=True)
    tmp_file = tmp_path / "custom1.log"
    if tmp_file.exists():
        os.remove(tmp_file)

    # ensure global variable "five" is reset to initial value
    global five
    five = 5

    # define custom event type that has an additional, required field (increment)
    class IncrementEvent(BaseEvent):
        increment: int

    try:
        eventit = EventLogger(
            directory=tmp_path, groups=["default", "custom1"], separate_files=True
        )

        # need to support dynamic args right now for metric function
        def increment_five(*args, **kwargs):
            global five
            five = five + 1
            return five

        eventit.register_custom_metric(metric="increment", func=increment_five)

        @eventit.event(
            group="custom1",
            tracking_details={
                "function_name": True,
                "group": False,
                "increment": True,
            },
            event_type=IncrementEvent,
        )
        def this_is_a_test():
            return "Hello, World"

        print(this_is_a_test())
        print(this_is_a_test())

        with open(tmp_file, "r", encoding="utf-8") as f:
            assert len(lines := f.readlines()) == 2
            first_line = json.loads(lines[0])
            assert first_line == {
                "timestamp": ANY,
                "uuid": ANY,
                "function_name": "this_is_a_test",
                "increment": 6,
            }
            second_line = json.loads(lines[1])
            assert second_line == {
                "timestamp": ANY,
                "uuid": ANY,
                "function_name": "this_is_a_test",
                "increment": 7,
            }

    finally:
        shutil.rmtree(tmp_path, ignore_errors=True)


def test_custom_metric_long(tmp_path):
    """Test basic funcitonality for custom metrics"""
    if tmp_path.exists():
        shutil.rmtree(tmp_path, ignore_errors=True)
    tmp_file = tmp_path / "custom1.log"
    if tmp_file.exists():
        os.remove(tmp_file)

    # ensure global variable "five" is reset to initial value
    global five
    five = 5

    # define custom event type that has an additional, required field (increment)
    class IncrementEvent(BaseEvent):
        increment: int

    try:
        eventit = EventLogger(
            directory=tmp_path, groups=["default", "custom1"], separate_files=True
        )
        start = time.time()

        # need to support dynamic args right now for metric function
        def increment_five(*args, **kwargs):
            global five
            five = five + 1
            return five

        eventit.register_custom_metric(metric="increment", func=increment_five)

        @eventit.event(
            group="custom1",
            tracking_details={
                "function_name": True,
                "group": False,
                "increment": True,
            },
            event_type=IncrementEvent,
        )
        def this_is_a_test():
            return "Hello, World"

        for _ in range(10000):
            this_is_a_test()

        with open(tmp_file, "r", encoding="utf-8") as f:
            assert len(lines := f.readlines()) == 10000
            for i in range(10000):
                line = json.loads(lines[i])
                assert line == {
                    "timestamp": ANY,
                    "uuid": ANY,
                    "function_name": "this_is_a_test",
                    "increment": i + 6,
                }
        end = time.time()

        # basic sanity check to ensure we don't get out of hand here.
        # should comfortably init and run within 0.5 seconds
        assert (end - start) < 0.5

    finally:
        shutil.rmtree(tmp_path, ignore_errors=True)
