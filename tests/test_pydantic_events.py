from eventit_py.pydantic_events import BaseEvent


def test_base_event_timestamp_uniqueness():
    event1 = BaseEvent()
    event2 = BaseEvent()

    assert event1.timestamp != event2.timestamp
