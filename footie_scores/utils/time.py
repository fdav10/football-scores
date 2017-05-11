''' Utilities for time and datetime operations '''

import logging
import datetime as dt
from datetime import datetime, timedelta

import pytz


logger = logging.getLogger(__name__)
TIME_FORMAT = '%Y-%m-%dT%H:%M:%S'


def datetime_string_make_aware(datetime_string, dt_format):
    return datetime.strptime(datetime_string, dt_format).astimezone()


def naive_utc_to_uk_tz(sdate, stime, date_format, time_format):
    ''' Convert a UTC time string to UK timezone.

    Date seems to need to be involved otherwise there's a bug (?)
    where changing the timezone offsets the minutes rather than
    hours.
    '''
    # TODO use dummy date
    # date is irrelevant to this function and only included to avoid
    # an apparent bug. Remove from arguments and use a dummy date
    # instead.
    f_date = dt.datetime.strptime(sdate, date_format)
    f_time = dt.datetime.strptime(stime, time_format).time()
    dt_ = dt.datetime.combine(f_date, f_time)
    utc_time = pytz.utc.localize(dt_)
    local_tz = pytz.timezone('Europe/London')
    local_time = utc_time.astimezone(local_tz)
    return local_time.strftime('%H:%M')


def time_from_now(minutes):
    return datetime.now() + timedelta(minutes=minutes)


def stime_from_now(minutes, time_format=TIME_FORMAT):
    return time_from_now(minutes).strftime(time_format)


def json_expiry_as_datime(json_data, time_format=TIME_FORMAT):
    return datetime.strptime(json_data['expiry_time'], time_format)


def time_elapsed_from(from_time):
    return from_time - datetime.now()
