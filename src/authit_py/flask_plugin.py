import datetime
import json
import logging
from typing import Any

from flask import Blueprint, request

from authit_py.base_plugin import BaseAuthitPlugin
from authit_py.pydantic_events import BaseEvent

logger = logging.getLogger(__name__)


class AuthitFlaskExtension(BaseAuthitPlugin):
    def __init__(self, app=None, url_prefix: str = "/authit", **kwargs) -> None:
        self.authit_api = None

        if app is not None:
            self.init_app(app, url_prefix=url_prefix)

        super().__init__(**kwargs)

    def init_app(self, app, url_prefix: str = "/authit"):
        self.authit_api = Blueprint(
            name="authit", import_name=__name__, url_prefix=url_prefix
        )

        @self.authit_api.route("/api/version")
        def get_authit_api_version():
            return "v0.1"

        app.register_blueprint(self.authit_api)
        # pass

    def retrieve_metric(self, metric: str) -> Any:
        match metric:
            case "timestamp":
                return datetime.datetime.now(tz=datetime.timezone.utc)
            case "route":
                return request.path
            case _:
                # in the future support custom metrics/data to log
                return None

    def track_metrics(self, func, tracking_details: dict[str, bool] = None):
        # @functools.wraps(func)
        def wrapper(*args, **kwargs):
            inner_tracking_details = tracking_details
            if tracking_details is None:
                inner_tracking_details = {
                    "route": True,
                    "timestamp": True,
                }
            api_event_details = {}
            for metric, should_track in inner_tracking_details.items():
                if not should_track:
                    continue
                api_event_details[metric] = self.retrieve_metric(metric=metric)

            # make event from details
            event = BaseEvent(**api_event_details)

            # log to chosen db client
            if self.chosen_backend == "filepath":
                json.dump(event.toJSON(), self.db_client)
            else:
                raise NotImplementedError(
                    f"Chosen backend {self.chosen_backend} unimplemented"
                )
            return func(*args, **kwargs)

        return wrapper
