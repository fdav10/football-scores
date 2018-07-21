

import os
from collections import namedtuple

from footie_scores import REPO_ROOT

LogRecord = namedtuple('LogRecord', ['url', 'time'])


class LogTable(list):
    def __init__(self, items):
        super(LogTable, self).__init__(items)

    def purge_old_records(self, minutes):
        pass


def log_to_table():
    with open(os.path.join(REPO_ROOT, 'logs', 'hourly_requests.log'), 'r') as log_file:
        data = log_file.read()
    table = [LogRecord(*l.split('\t')) for l in data.splitlines()]
    import ipdb; ipdb.set_trace()


if __name__ == '__main__':
    log_to_table()
