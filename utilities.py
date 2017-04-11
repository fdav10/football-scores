''' Utilities for football scores '''

from datetime import datetime


def datetime_string_make_aware(datetime_string, dt_format):
    return datetime.strptime(datetime_string, dt_format).astimezone()
