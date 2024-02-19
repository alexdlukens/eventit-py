import json
import os
from unittest.mock import ANY

from eventit_py.event_logger import EventLogger

# cur_path = pathlib.Path(__file__)
# sys.path.insert(0, cur_path.parent.parent)


def test_event_logger_setup(tmp_path):
    # from authit_py.flask_plugin import AuthitFlaskExtension

    tmp_file = tmp_path / "eventit.log"
    if tmp_file.exists():
        os.remove(tmp_file)

    try:
        eventit = EventLogger(filepath=str(tmp_file))

        assert eventit.filepath == str(tmp_file)
        assert tmp_file.exists()

    finally:
        os.remove(tmp_file)


def test_event_logger_single_event(tmp_path):
    # from authit_py.flask_plugin import AuthitFlaskExtension

    tmp_file = tmp_path / "eventit.log"
    if tmp_file.exists():
        os.remove(tmp_file)

    try:
        eventit = EventLogger(filepath=str(tmp_file))

        assert eventit.filepath == str(tmp_file)
        assert tmp_file.exists()

        @eventit.event(tracking_details={"timestamp": True})
        def this_is_a_test():
            return "Hello, World"

        print(this_is_a_test())

        with open(tmp_file, "r", encoding="utf-8") as f:
            assert len(lines := f.readlines()) == 1
            first_line = json.loads(lines[0])
            assert first_line == {"timestamp": ANY, "user": None, "group": None}

    finally:
        os.remove(tmp_file)
