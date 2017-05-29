''' Utilities for time and datetime operations '''

import logging
import datetime as dt
from datetime import datetime, timedelta

import pytz

from footie_scores.settings import OVERRIDE_TIME, OVERRIDE_DAY


logger = logging.getLogger(__name__)
TIME_FORMAT = '%Y-%m-%dT%H:%M:%S'


def today(override_day=OVERRIDE_DAY):
    if override_day:
        logger.warning("Override day %s passed to today() function", override_day)
        return override_day
    else:
        return dt.date.today()


def now(override_time=OVERRIDE_TIME):
    if override_time:
        logger.warning("Override time %s passed to now() function", override_time)
        return dt.datetime.combine(today(), override_time)
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
