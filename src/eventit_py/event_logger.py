import functools
import logging
from typing import Any, Callable

from eventit_py.base_logger import BaseEventLogger
from eventit_py.pydantic_events import BaseEvent

logger = logging.getLogger(__name__)


class EventLogger(BaseEventLogger):
    def retrieve_metric(
        self, metric: str, func: Callable = None, context: dict[str, Any] = None
    ) -> Any:
        """Function where new metric retrieval code should be implemented.

        Args:
            metric (str): _description_
            func (Callable, optional): _description_. Defaults to None.

        Raises:
            NotImplementedError: If retrieve_metric unimplemented for the specified metric

        Returns:
            Any: The computed metric
        """
        if metric in self.builtin_metrics:
            return self.builtin_metrics[metric](func=func, context=context)
        elif metric in self.custom_metrics:
            return self.custom_metrics[metric](func=func, context=context)
        raise NotImplementedError(
            f"retrieve_metric unimplemented for metric '{metric}'"
        )

    def register_custom_metric(self, metric: str, func: Callable):
        """Register a user-defined metric on name provided, to be retrieved using provided function

        Args:
            metric (str): name of new metric
            func (Callable): function to retrieve specified metric

        Raises:
            ValueError: If metric specified by name already present in builtin_metrics or custom_metrics
        """
        if metric in self.builtin_metrics:
            raise ValueError(f"Metric '{metric}' already present in builtin metrics")
        elif metric in self.custom_metrics:
            raise ValueError(
                f"Metric '{metric}' registered multiple times as custom metric"
            )
        self.custom_metrics[metric] = func

    def log_event(
        self,
        func: Callable = None,
        description: str = None,
        tracking_details: dict[str, bool] = None,
        event_type: Callable = None,
        group: str = None,
    ) -> None:
        """Main function used to log information. Inherits builtin metrics from BaseEventLogger

        Args:
            func (Callable, optional): Function that produced event we are logging. Defaults to None.
            description (str, optional): Description to be included with the event being logged
            tracking_details (dict[str, bool], optional): Specific metrics to be tracked. Defaults to tracking all builtin metrics.
            event_type (Callable): Event type (as pydantic model) used for pydantic type validation
        Raises:
            NotImplementedError: If logging backend specified in class constructor is not yet implemented
        """
        if event_type is None:
            event_type = self._default_event_type
        if group is None:
            group = self._default_event_group
        if not issubclass(event_type, BaseEvent):
            raise TypeError(
                f"provided event type {event_type} is not derived from {self._default_event_type}"
            )
        inner_tracking_details = tracking_details
        # default to providing all builtin metrics if no specific metrics provided to track
        if tracking_details is None:
            inner_tracking_details = {metric: True for metric in self.builtin_metrics}
        api_event_details = {}
        api_event_details["description"] = description

        # would add additional fields into context as metrics get more complex
        tracking_context = {"group": group}

        for metric, should_track in inner_tracking_details.items():
            if not should_track:
                continue
            api_event_details[metric] = self.retrieve_metric(
                metric=metric, func=func, context=tracking_context
            )

        # make event from details
        event = event_type(**api_event_details)

        # log to chosen db client
        self.db_client.log_message(message=event, group=group)

    def event(
        self,
        func: Callable = None,
        description: str = None,
        tracking_details: dict[str, bool] = None,
        event_type: Callable = None,
        group=None,
    ) -> Callable:
        """Wrapper to be placed around functions that want logging functionality before they are called

        Args:
            func (Callable, optional): Function to be wrapped
            description (str, optional): Description to be included with the event being logged
            tracking_details (dict[str, bool], optional): Specific metrics to be tracked. Defaults to tracking all builtin metrics.
            event_type (Callable): Event type (as pydantic model) used for pydantic type validation

        Raises:
            NotImplementedError: If logging backend specified in class constructor is not yet implemented

        Returns:
            Callable: wrapped function
        """
        if func is None:
            return functools.partial(
                self.event,
                description=description,
                tracking_details=tracking_details,
                event_type=event_type,
                group=group,
            )

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # defer to log_event function for specific handling
            self.log_event(
                func=func,
                description=description,
                tracking_details=tracking_details,
                event_type=event_type,
                group=group,
            )

            return func(*args, **kwargs)

        return wrapper
