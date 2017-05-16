''' Utilities for time and datetime operations '''

import logging
import datetime as dt
from datetime import datetime, timedelta

import pytz


logger = logging.getLogger(__name__)
TIME_FORMAT = '%Y-%m-%dT%H:%M:%S'


def datetime_string_make_aware(datetime_string, dt_format):
    return datetime.strptime(datetime_string, dt_format).astimezone()


def naive_utc_to_uk_tz(stime, time_format, desired_time_format='%H:%M'):
    ''' Convert a UTC time string to UK timezone. '''
    f_date = dt.date(2017, 5, 1)
    f_time = dt.datetime.strptime(stime, time_format).time()
    dt_ = dt.datetime.combine(f_date, f_time)
    utc_time = pytz.utc.localize(dt_)
    local_tz = pytz.timezone('Europe/London')
    local_time = utc_time.astimezone(local_tz)
    return local_time.strftime(desired_time_format)


def time_from_now(minutes):
    return datetime.now() + timedelta(minutes=minutes)


def stime_from_now(minutes, time_format=TIME_FORMAT):
    return time_from_now(minutes).strftime(time_format)


def json_expiry_as_datime(json_data, time_format=TIME_FORMAT):
    return datetime.strptime(json_data['expiry_time'], time_format)


def time_elapsed_from(from_time):
    return from_time - datetime.now()
