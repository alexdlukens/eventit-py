import os
import pathlib
import traceback

import pytest
from authit_py.flask_plugin import AuthitFlaskExtension

# cur_path = pathlib.Path(__file__)
# sys.path.insert(0, cur_path.parent.parent)


def test_flask_server(client):
    app = client

    try:
        resp = app.get("/")

        assert resp.status_code == 200

    except Exception():
        pytest.fail("Exception while testing flask server")


def test_flask_extension_setup(flask_setup, tmp_path):
    # from authit_py.flask_plugin import AuthitFlaskExtension

    tmp_file = tmp_path / "authit.log"
    if tmp_file.exists():
        os.remove(tmp_file)

    app = flask_setup
    client = app.test_client()

    authit = AuthitFlaskExtension(filepath=str(tmp_file))
    authit.init_app(app, url_prefix="/banana")

    try:
        resp = client.get("/banana/api/version")

        assert resp.status_code == 200
        assert resp.text == "v0.1"

    except Exception():
        pytest.fail("Exception while testing flask server")
    finally:
        os.remove(tmp_file)


def test_flask_extension_filepath_route(flask_setup, tmp_path: pathlib.Path):
    # from authit_py.flask_plugin import AuthitFlaskExtension
    tmp_file = tmp_path / "authit.log"
    if tmp_file.exists():
        os.remove(tmp_file)

    app = flask_setup
    client = app.test_client()

    authit = AuthitFlaskExtension(filepath=str(tmp_file))
    authit.init_app(app, url_prefix="/banana")

    assert tmp_file.is_file()
    assert tmp_file.read_text() == ""  # make sure file starts empty

    @app.route("/this_is_a_test")
    @authit.track_metrics
    def this_is_a_test_route():
        return "hello_world", 201

    assert tmp_file.read_text() == ""  # file should still be empty

    try:
        resp = client.get("/banana/api/version")

        assert resp.status_code == 200
        assert resp.text == "v0.1"

        resp2 = client.get("/this_is_a_test")
        assert resp2.status_code == 201
        assert resp2.text == "hello_world"

        authit.db_client.flush()
        if tmp_file.read_text() == "":
            # nothing got logged
            pytest.fail("Nothing was logged to filepath from extension")

    except AssertionError:
        traceback.print_exc()
        raise
    except Exception:
        pytest.fail("Exception while testing flask server")
    finally:
        os.remove(tmp_file)
