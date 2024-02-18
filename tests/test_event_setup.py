import os

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
