import json
import logging
from typing import Any

from eventit_py.pydantic_events import BaseEvent
from eventit_py.base_logger import BaseEventLogger

logger = logging.getLogger(__name__)


class EventLogger(BaseEventLogger):
    def retrieve_metric(self, metric: str) -> Any:
        raise NotImplementedError("retrieve_metric unimplemented")

    def event(self, func, tracking_details: dict[str, bool] = None):
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
                json.dump(event.model_dump(mode="json"), self.db_client)
            else:
                raise NotImplementedError(
                    f"Chosen backend {self.chosen_backend} unimplemented"
                )
            return func(*args, **kwargs)

        return wrapper
