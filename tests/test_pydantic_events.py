import time

from eventit_py.pydantic_events import BaseEvent


def test_base_event_timestamp_uniqueness():
    event1 = BaseEvent()
    time.sleep(0.01)
    event2 = BaseEvent()

    assert event1.timestamp != event2.timestamp


def test_base_event_uuid_uniqueness():
    event1 = BaseEvent()
    time.sleep(0.01)
    event2 = BaseEvent()

    assert event1.uuid != event2.uuid
