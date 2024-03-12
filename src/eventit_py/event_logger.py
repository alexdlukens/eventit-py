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

        This method is used to log information about an event. It takes in various parameters such as the function that produced the event,
        a description of the event, specific metrics to be tracked, the event type, and the event group. If no event type is provided,
        it defaults to the default event type specified in the class. If no event group is provided, it defaults to the default event group
        specified in the class.

        The method first checks if the provided event type is derived from the default event type. If not, it raises a TypeError.
        It then prepares the tracking details by either using the provided tracking details or tracking all builtin metrics if none are provided.
        It creates a dictionary `api_event_details` to store the event details, including the description. It also creates a `tracking_context`
        dictionary to store additional context information for tracking.

        The method then iterates over the tracking details and retrieves the corresponding metrics using the `retrieve_metric` method.
        The retrieved metrics are added to the `api_event_details` dictionary.

        Finally, an event object is created using the event type and the `api_event_details` dictionary. The event is then logged to the
        chosen database client using the `log_message` method of the `db_client`.

        Note: This method assumes the existence of a `db_client` attribute in the class, which is responsible for logging the event.

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
            group: Group identifier for the event

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
