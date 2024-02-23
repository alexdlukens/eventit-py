import json
import os
import shutil
from unittest.mock import ANY

from eventit_py.event_logger import EventLogger
from eventit_py.pydantic_events import BaseEvent

# cur_path = pathlib.Path(__file__)
# sys.path.insert(0, cur_path.parent.parent)
five = 5


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

    # define custom event type that has an additional, required field (increment)
    class IncrementEvent(BaseEvent):
        increment: int

    try:
        eventit = EventLogger(
            directory=tmp_path, groups=["default", "custom1"], separate_files=True
        )

        def increment_five(*args, **kwargs):
            global five
            five = five + 1
            return five

        eventit.register_custom_metric(metric="increment", func=increment_five)

        @eventit.event(
            group="custom1",
            tracking_details={
                "timestamp": True,
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
                "function_name": "this_is_a_test",
                "increment": 6,
            }
            second_line = json.loads(lines[1])
            assert second_line == {
                "timestamp": ANY,
                "function_name": "this_is_a_test",
                "increment": 7,
            }

    finally:
        shutil.rmtree(tmp_path, ignore_errors=True)
