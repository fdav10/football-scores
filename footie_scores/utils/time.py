''' Utilities for time and datetime operations '''

import logging
import datetime as dt
from datetime import datetime, timedelta

import pytz

from footie_scores.settings import OVERRIDE_TIME, OVERRIDE_DAY, START_TIME


logger = logging.getLogger(__name__)
TIME_FORMAT = '%Y-%m-%dT%H:%M:%S'


def today(override_day=OVERRIDE_DAY):
    if override_day:
        time_elapsed = dt.datetime.now() - START_TIME
        return override_day + time_elapsed
    else:
        return dt.date.today()


def now(override_time=OVERRIDE_TIME):
    if override_time:
        time_elapsed = dt.datetime.now() - START_TIME
        return dt.datetime.combine(today(), override_time) + time_elapsed
    else:
        return dt.datetime.now()


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


def chop_microseconds(tdelta):
    return tdelta - dt.timedelta(microseconds=tdelta.microseconds)



def custom_strftime(dt_format, t):
    # credit to https://stackoverflow.com/a/5891598
    def suffix(d):
        return 'th' if 11 <= d <= 13 else {1:'st', 2:'nd', 3:'rd'}.get(d%10, 'th')

    assert '%d' in dt_format, 'Expecting a %d directive'
    custom_format = dt_format.replace('%d', '{S}')
    return t.strftime(custom_format).replace('{S}', str(t.day) + suffix(t.day))


if OVERRIDE_DAY:
    logger.warning(
        "utils.time.today() function returning %s rather than today's date", today())
if OVERRIDE_TIME:
    logger.warning(
        "utils.time.now() function returning %s rather than time now", now())
