''' Utilities for time and datetime operations '''

import logging
from datetime import datetime, timedelta


logger = logging.getLogger(__name__)
TIME_FORMAT = '%Y-%m-%dT%H:%M:%S'


def datetime_string_make_aware(datetime_string, dt_format):
    # return datetime.strptime(datetime_string, dt_format).astimezone()
    return datetime.strptime(datetime_string, dt_format)


def time_from_now(minutes):
    return datetime.now() + timedelta(minutes=minutes)


def stime_from_now(minutes, time_format=TIME_FORMAT):
    return time_from_now(minutes).strftime(time_format)


def json_expiry_as_datime(json_data, time_format=TIME_FORMAT):
    return datetime.strptime(json_data['expiry_time'], time_format)


def time_elapsed_from(from_time):
    return from_time - datetime.now()
