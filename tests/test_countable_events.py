import datetime
import time

from bson.codec_options import CodecOptions
from eventit_py.event_logger import EventLogger
from eventit_py.pydantic_events import (
    BaseCountableEvent,
    _handle_timestamp,
    _subtract_time_delta,
)
from pymongo import MongoClient

EVENTIT_DB_NAME = "eventit"


# create class derived from BaseCountableEvent called TenSecondCounter
class TenSecondCounter(BaseCountableEvent):
    time_window: int = 10


def test_ten_second_counter(get_mongo_uri):
    mongo_client = MongoClient(get_mongo_uri)

    eventit = EventLogger(MONGO_URL=get_mongo_uri, database=EVENTIT_DB_NAME)

    @eventit.event(
        description="This is a basic test for MongoDB", event_type=TenSecondCounter
    )
    def this_is_a_mongodb_test():
        return -1

    pre_start_time = _handle_timestamp()

    time_window = TenSecondCounter.model_fields["time_window"].default
    time_window = datetime.timedelta(seconds=time_window)
    assert time_window.total_seconds() == 10

    _, remainder = _subtract_time_delta(pre_start_time, time_window)

    # wait for remainder to be up
    sleep_time = time_window - remainder

    assert sleep_time < time_window
    assert remainder.total_seconds() < 10

    print(f"waiting {sleep_time} for next time window")
    time.sleep(sleep_time.total_seconds() + 0.1)
    # now we should be in the next time window

    start_time = _handle_timestamp()

    base_time_window, remainder = _subtract_time_delta(start_time, time_window)

    for i in range(10):
        this_is_a_mongodb_test()
        time.sleep(0.1)

    end_time = _handle_timestamp()

    end_time_window, remainder = _subtract_time_delta(end_time, time_window)

    assert base_time_window == end_time_window

    # get event from db corresponding to base_time_window
    event = (
        mongo_client[EVENTIT_DB_NAME]["default"]
        .with_options(CodecOptions(tz_aware=True))
        .find_one({"timestamp": base_time_window})
    )

    # check that the event has 10 entries
    assert event["count"] == 10

    end_time2 = _handle_timestamp()
    _, remainder = _subtract_time_delta(end_time2, time_window)
    # wait for remainder to be up AGAIN
    sleep_time = time_window - remainder

    assert sleep_time < time_window
    assert remainder.total_seconds() < 10

    print(f"waiting {sleep_time} for next time window")
    time.sleep(sleep_time.total_seconds() + 0.1)

    end_time3 = _handle_timestamp()
    second_time_window, _ = _subtract_time_delta(end_time3, time_window)
    # now we should be in the next time window, ensure that a new time window event is created
    for i in range(15):
        this_is_a_mongodb_test()
        time.sleep(0.1)

    # get event from db corresponding to base_time_window
    event1 = (
        mongo_client[EVENTIT_DB_NAME]["default"]
        .with_options(CodecOptions(tz_aware=True))
        .find_one({"timestamp": base_time_window})
    )
    event2 = (
        mongo_client[EVENTIT_DB_NAME]["default"]
        .with_options(CodecOptions(tz_aware=True))
        .find_one({"timestamp": second_time_window})
    )
    print(f"{event1=}, {event2=}, {base_time_window=}, {second_time_window=}")
    assert event1["count"] == 10
    assert event2["count"] == 15

    # ensure the event can be validated into Pydantic model
    TenSecondCounter.model_validate(event)
