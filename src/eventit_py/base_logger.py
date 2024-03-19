import inspect
import logging
import pathlib
from typing import Callable, Union

from eventit_py.logging_backends import FileLoggingClient, MongoDBLoggingClient
from eventit_py.pydantic_events import BaseEvent

logger = logging.getLogger(__name__)

DEFAULT_LOG_FILEPATH = "eventit.log"


def _get_external_location(*args, **kwargs) -> str:
    """
    Returns the location of the calling function.

    Args:
        *args: Variable length argument list.
        **kwargs: Arbitrary keyword arguments.

    Returns:
        str: The location of the calling function.
    """
    caller_frame = inspect.currentframe().f_back
    frame_info = inspect.getframeinfo(caller_frame)

    # check if the function is called from within eventit_py
    while "eventit_py" in frame_info.filename:
        caller_frame = caller_frame.f_back
        if caller_frame is None:
            return None
        frame_info = inspect.getframeinfo(caller_frame)

    # Get the module name
    module_name = inspect.getmodulename(frame_info.filename)
    if module_name is None:
        module_name = pathlib.Path(frame_info.filename).name

    # Get the package name
    package_name = module_name.split(".")[0] if "." in module_name else module_name
    if package_name == module_name:
        location_string = f"{module_name}:{frame_info.function}"
    else:
        location_string = f"{package_name}.{module_name}:{frame_info.function}"

    return location_string


def _return_function_name(func: Callable, *args, **kwargs) -> Union[str, None]:
    """
    Returns the name of the given function.

    Args:
        func (Callable): The function to get the name of.
        *args: Variable length argument list.
        **kwargs: Arbitrary keyword arguments.

    Returns:
        Union[str, None]: The name of the function as a string, or None if the function is None.

    """
    try:
        return func.__name__
    except AttributeError:
        if func is None:
            return None
        return str(func)


def _return_group(func: Callable, *args, **kwargs) -> Union[str, None]:
    """
    Returns the 'group' value from the 'context' dictionary if it exists, otherwise returns None.

    Args:
        func (Callable): The function to be called.
        *args: Variable length argument list.
        **kwargs: Arbitrary keyword arguments.

    Returns:
        Union[str, None]: The 'group' value from the 'context' dictionary if it exists, otherwise None.
    """
    if "context" in kwargs:
        context: dict = kwargs["context"]
        return context.get("group", None)
    return None


class BaseEventLogger:
    """
    Base class for event logging.

    This class provides a base implementation for event logging and serves as a template for subclasses to implement
    specific logging functionality.

    Args:
        default_event_type (Callable, optional): The default event type to be used if not provided. Defaults to None.
        ``**kwargs``: Additional keyword arguments for configuring the logger.

    Attributes:
        _default_event_type (Callable): The default event type.
        chosen_backend (str): The chosen backend for logging.
        db_client: The database client for logging.
        groups (list[str]): The list of event groups.
        _default_event_group (str): The default event group.
        builtin_metrics (dict[str, Callable]): The dictionary of built-in metrics.
        custom_metrics (dict[str, Callable]): The dictionary of custom metrics.

    """

    def __init__(self, default_event_type: Callable = None, **kwargs) -> None:
        self._default_event_type = default_event_type
        if default_event_type is None:
            self._default_event_type = BaseEvent
        self.chosen_backend = None
        self.db_client = None
        self.groups: list[str] = kwargs.get("groups", ["default"])
        self._default_event_group = kwargs.get("default_event_group", "default")
        self.groups.append(self._default_event_group)
        self.groups = list(set(self.groups))
        self.required_metrics = set(["timestamp", "uuid"])
        self.builtin_metrics: dict[str, Callable] = {
            "function_name": _return_function_name,
            "group": _return_group,
            "event_location": _get_external_location,
        }

        self.custom_metrics: dict[str, Callable] = {}

        logger.debug("In BaseEventLogger Constructor")
        if "MONGO_URL" in kwargs:
            self.chosen_backend = "mongodb"
            mongo_url = kwargs.get("MONGO_URL")
            database_name = kwargs.get("database_name")
            self.db_client = MongoDBLoggingClient(
                mongo_url=mongo_url, database_name=database_name, groups=self.groups
            )

        # at end, default to using filepath if no other log specified
        if not self.chosen_backend or "directory" in kwargs:
            logger.debug("setting up filepath backend")
            self.chosen_backend = "filepath"
            directory = pathlib.Path(kwargs.get("directory", "./"))
            if not directory.exists():
                directory.mkdir(parents=True)
            self.db_client = FileLoggingClient(
                directory=kwargs.get("directory", "./"),
                groups=self.groups,
                separate_files=kwargs.get("separate_files", True),
                filename=kwargs.get("filename"),
            )

        logger.debug("BaseEventLogger configuration complete")

    def register_custom_metric(self, metric: str, func: Callable):
        """Register a user-defined metric on name provided, to be retrieved using provided function

        Args:
            metric (str): name of new metric
            func (Callable): function to retrieve specified metric

        Raises:
            ValueError: If metric specified by name already present in builtin_metrics or custom_metrics
        """
        if metric in self.required_metrics:
            raise ValueError(f"Metric '{metric}' already present in required metrics")
        if metric in self.builtin_metrics:
            raise ValueError(f"Metric '{metric}' already present in builtin metrics")
        if metric in self.custom_metrics:
            raise ValueError(
                f"Metric '{metric}' registered multiple times as custom metric"
            )
        self.custom_metrics[metric] = func

    def log_event(self):
        raise NotImplementedError(
            "log_event() wrapper unimplemented in BaseEventLogger"
        )

    def event(self):
        """Wrapper function to be implemented in subclass"""
        raise NotImplementedError("event() wrapper unimplemented in BaseEventLogger")
