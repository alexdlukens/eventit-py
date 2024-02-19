import json
import os
from unittest.mock import ANY

import pytest
from eventit_py.event_logger import EventLogger


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