from eventit_py.base_logger import BaseEventLogger
from eventit_py.pydantic_events import BaseEvent


class MyEvent2(BaseEvent):
    special_field: str


def test_init_default_event_type():
    default_event_type = MyEvent2
    logger = BaseEventLogger(default_event_type=default_event_type)
    assert logger._default_event_type == default_event_type


def test_init_default_event_type_none():
    logger = BaseEventLogger()
    assert logger._default_event_type == BaseEvent


def test_init_default_event_group():
    default_event_group = "default_group"
    logger = BaseEventLogger(default_event_group=default_event_group)
    assert logger._default_event_group == default_event_group


def test_init_default_event_group_none():
    logger = BaseEventLogger()
    assert logger._default_event_group == "default"


def test_init_groups():
    groups = ["group1", "group2"]
    logger = BaseEventLogger(groups=groups)
    assert sorted(logger.groups) == sorted(groups)


def test_init_groups_empty():
    logger = BaseEventLogger()
    assert logger.groups == ["default"]


def test_init_builtin_metrics():
    logger = BaseEventLogger()
    assert sorted(logger.builtin_metrics.keys()) == [
        "event_location",
        "function_name",
        "group",
        "timestamp",
    ]


def test_init_custom_metrics():
    def metric1_func(*args, **kwargs):
        return -1

    # custom_metrics = {"metric1": metric1_func}
    logger = BaseEventLogger()
    logger.register_custom_metric("metric1", metric1_func)
    assert "metric1" in logger.custom_metrics


def test_init_custom_metrics_empty():
    logger = BaseEventLogger()
    assert len(logger.custom_metrics) == 0
