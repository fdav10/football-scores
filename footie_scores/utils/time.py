''' Utilities for time and datetime operations '''

import logging, sys
import datetime as dt
from datetime import datetime, timedelta

import pytz

from footie_scores import constants
from footie_scores.settings import OVERRIDE_TIME, OVERRIDE_DAY, START_TIME, DB_DATEFORMAT


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
        time_elapsed = dt.datetime.utcnow(tz) - START_TIME
        return dt.datetime.combine(today(), override_time) + time_elapsed
    else:
        return dt.datetime.utcnow()


def datetime_string_make_aware(datetime_string, dt_format):
    return datetime.strptime(datetime_string, dt_format).astimezone()


def reformat_datetime(sdatetime, format_in, format_as='%H:%M'):
    date_and_time = dt.datetime.strptime(sdatetime, format_as)
    return dt.datetime.strftime(date_and_time, format_as)


def chop_microseconds(tdelta):
    return tdelta - dt.timedelta(microseconds=tdelta.microseconds)


def custom_strftime(dt_format, t):
    # credit to https://stackoverflow.com/a/5891598
    def suffix(d):
        return 'th' if 11 <= d <= 13 else {1:'st', 2:'nd', 3:'rd'}.get(d%10, 'th')

    assert '%d' in dt_format, 'Expecting a %d directive'
    custom_format = dt_format.replace('%d', '{S}')
    return t.strftime(custom_format).replace('{S}', str(t.day) + suffix(t.day))


def month_list_define_first(first_month_num, month_list=constants.MONTHS):
    '''
    Rearrange a Jan-Dec month list so that the first list element is
    that indicated by first_month_num (1-12 - not an index) and the
    remaining months follow in order, looping around if necessary.
    '''
    head = month_list[first_month_num-1:]
    tail = month_list[:first_month_num-1]
    return head + tail


def month_list_define_last(first_month_num, month_list=constants.MONTHS):
    '''
    Rearrange a Jan-Dec month list so that the last list element is
    that indicated by first_month_num (1-12 - not an index) and the
    remaining months precede in order, looping around if necessary.
    '''
    first_month = month_list[first_month_num-1]
    head = month_list[first_month_num:]
    tail = month_list[:first_month_num-1] + (first_month,)
    return head + tail


def validate_date_str(date_str, dateformat=DB_DATEFORMAT):
    try:
        dt.datetime.strptime(date_str, dateformat)
    except ValueError as e:
        example_format = dt.datetime.strftime(today(), dateformat)
        sys.tracebacklimit = None
        raise ValueError(
            'Incorrect date format. Should be in form, e.g.: {}'.format(example_format)) from None


if OVERRIDE_DAY:
    logger.warning(
        "utils.time.today() function returning %s rather than today's date", today())
if OVERRIDE_TIME:
    logger.warning(
        "utils.time.now() function returning %s rather than time now", now())
