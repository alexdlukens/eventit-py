import functools
import json
import logging
from typing import Any, Callable

from eventit_py.base_logger import BaseEventLogger
from eventit_py.pydantic_events import BaseEvent

logger = logging.getLogger(__name__)


class EventLogger(BaseEventLogger):
    def retrieve_metric(self, metric: str, func: Callable = None) -> Any:
        """Function where new metric retrieval code should be implemented.

        Args:
            metric (str): _description_
            func (Callable, optional): _description_. Defaults to None.

        Raises:
            NotImplementedError: _description_

        Returns:
            Any: _description_
        """
        if metric in self.builtin_metrics:
            return self.builtin_metrics[metric](func=func)

        raise NotImplementedError("retrieve_metric unimplemented")

    def log_event(
        self, func: Callable = None, tracking_details: dict[str, bool] = None
    ) -> None:
        """Main function used to log information. Inherits builtin metrics from BaseEventLogger

        Args:
            func (Callable, optional): Function that produced event we are logging. Defaults to None.
            tracking_details (dict[str, bool], optional): Specific metrics to be tracked. Defaults to tracking all builtin metrics.

        Raises:
            NotImplementedError: If logging backend specified in class constructor is not yet implemented
        """
        inner_tracking_details = tracking_details
        # default to providing all metrics if no specific metrics provided to track
        if tracking_details is None:
            inner_tracking_details = {metric: True for metric in self.builtin_metrics}
        api_event_details = {}
        for metric, should_track in inner_tracking_details.items():
            if not should_track:
                continue
            api_event_details[metric] = self.retrieve_metric(metric=metric, func=func)

        # make event from details
        event = BaseEvent(**api_event_details)

        # log to chosen db client
        if self.chosen_backend == "filepath":
            json.dump(event.model_dump(mode="json", exclude_none=True), self.db_client)
            self.db_client.flush()
        else:
            raise NotImplementedError(
                f"Chosen backend {self.chosen_backend} unimplemented"
            )

    def event(
        self, func: Callable = None, tracking_details: dict[str, bool] = None
    ) -> Callable:
        """Wrapper to be placed around functions that want logging functionality before they are called

        Args:
            func (Callable, optional): Function to be wrapped
            tracking_details (dict[str, bool], optional): Specific metrics to be tracked. Defaults to tracking all builtin metrics.

        Raises:
            NotImplementedError: If logging backend specified in class constructor is not yet implemented

        Returns:
            Callable: wrapped function
        """
        if func is None:
            return functools.partial(self.event, tracking_details=tracking_details)

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # defer to log_event function for specific handling
            self.log_event(func=func, tracking_details=tracking_details)

            return func(*args, **kwargs)

        return wrapper
