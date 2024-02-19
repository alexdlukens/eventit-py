import os

import pytest
from eventit_py.event_logger import EventLogger
from pydantic import ValidationError


def test_bad_event_type(tmp_path):
    tmp_file = tmp_path / "eventit.log"
    if tmp_file.exists():
        os.remove(tmp_file)

    eventit = EventLogger(filepath=str(tmp_file))

    assert eventit.filepath == str(tmp_file)
    assert tmp_file.exists()

    # log event with specific name
    try:
        eventit.log_event("Banana", event_type=dict)
        pytest.fail("log event did not break with invalid event type")
    except TypeError:
        pass  # we expected this to happen


def test_bad_description_type(tmp_path):
    tmp_file = tmp_path / "eventit.log"
    if tmp_file.exists():
        os.remove(tmp_file)

    eventit = EventLogger(filepath=str(tmp_file))

    assert eventit.filepath == str(tmp_file)
    assert tmp_file.exists()

    # log event with specific name
    try:
        # description is of bad type
        eventit.log_event(description=42)
        pytest.fail("log event did not break with bad description type")
    except ValidationError:
        pass  # we expected this to happen
