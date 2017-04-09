''' Utilities for football scores '''


from datetime import datetime


DT_FORMAT = "%Y-%m-%dT%H:%M:%SZ"


def fixture_datetime(fixture):
    ''' datetime.datetime object for fixture '''
    raw = fixture['date']
    return datetime.strptime(raw, DT_FORMAT)


def fixture_time(fixture):
    ''' datetime.time object for fixture '''
    f_datetime = fixture_datetime(fixture)
    return f_datetime.time()


def fixture_date(fixture):
    ''' datetime.date object for fixture '''
    f_datetime = fixture_datetime(fixture)
    return f_datetime.date()
