import json
import os
import shutil
from unittest.mock import ANY

from eventit_py.event_logger import EventLogger


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
    if tmp_path.exists():
        shutil.rmtree(tmp_path, ignore_errors=True)

    try:
        eventit = EventLogger(directory=str(tmp_path))

        @eventit.event(tracking_details={"timestamp": True})
        def this_is_a_test():
            return "Hello, World"

        assert this_is_a_test() == "Hello, World"

        with open(tmp_file, "r", encoding="utf-8") as f:
            assert len(lines := f.readlines()) == 1
            first_line = json.loads(lines[0])
            assert first_line == {
                "timestamp": ANY,
            }

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

        assert this_is_a_test() == "Hello, World"

        with open(tmp_file, "r", encoding="utf-8") as f:
            assert len(lines := f.readlines()) == 1
            first_line = json.loads(lines[0])
            assert first_line == {
                "timestamp": ANY,
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
                "group": "default",
                "function_name": "Banana",
            }
            assert second_line == {"timestamp": ANY, "group": "default"}

    finally:
        shutil.rmtree(tmp_path, ignore_errors=True)


def test_setup_custom_group(tmp_path):
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

        assert this_is_a_test() == "Hello, World"

        with open(tmp_file, "r", encoding="utf-8") as f:
            assert len(lines := f.readlines()) == 1
            first_line = json.loads(lines[0])
            assert first_line == {
                "timestamp": ANY,
                "function_name": "this_is_a_test",
            }

    finally:
        shutil.rmtree(tmp_path, ignore_errors=True)


def test_setup_custom_group_single_file(tmp_path):
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

        assert this_is_a_test() == "Hello, World"
        assert this_is_a_test2() == "Hello, World2"

        with open(tmp_file, "r", encoding="utf-8") as f:
            assert len(lines := f.readlines()) == 2
            first_line = json.loads(lines[0])
            assert first_line == {
                "timestamp": ANY,
                "function_name": "this_is_a_test",
                "group": "custom1",
            }
            second_line = json.loads(lines[1])
            assert second_line == {
                "timestamp": ANY,
                "function_name": "this_is_a_test2",
                "group": "default",
            }

    finally:
        shutil.rmtree(tmp_path, ignore_errors=True)


def test_multiple_groups_single_file(tmp_path):
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

        assert this_is_a_test() == "Hello, World"

        with open(tmp_file, "r", encoding="utf-8") as f:
            assert len(lines := f.readlines()) == 1
            first_line = json.loads(lines[0])
            assert first_line == {
                "timestamp": ANY,
                "function_name": "this_is_a_test",
                "group": "custom1",
            }

    finally:
        shutil.rmtree(tmp_path, ignore_errors=True)
