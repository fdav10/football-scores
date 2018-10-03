

import os
from time import sleep
import datetime as dt
from collections import namedtuple

from footie_scores import REPO_ROOT
from footie_scores import utils


REQUESTS_LOG = os.path.join(REPO_ROOT, 'logs', 'hourly_requests.log')
REQUESTS_RATE_LOG = os.path.join(REPO_ROOT, 'logs', 'requests_rate.log')

SLEEP_TIME = 2 * 60 # two minutes in seconds
PURGE_OLDER_THAN = 60 * 60 # one hour in seconds

TIME_FORMAT =  "%Y-%m-%d %H:%M:%S.%f"


class LogRecord:
    def __init__(self, url, time):
        self.url = url
        self.time = time[:time.find('+')] # ignore timezone offset info (don't have to do this with Py37)
        self.datetime = dt.datetime.strptime(self.time, TIME_FORMAT).replace(tzinfo=None)

    def __repr__(self):
        return f"<LogRecord url='{self.url}' time='{self.time}'>"

class LogTable:
    def __init__(self, records):
        self._records = records
        self.times = [r.time for r in self._records]
        self.urls = [r.url for r in self._records]
        self.datetimes = [r.datetime for r in self._records]

    def log_requests_rate(self):
        self._purge_old_records(older_than=PURGE_OLDER_THAN)
        self._update_requests_rate_log()

    def _purge_old_records(self, older_than):
        ini_size = len(self._records)
        self._records = [record for record in self._records
                if (dt.datetime.utcnow() - record.datetime).total_seconds()
                <= older_than]

        if ini_size != len(self._records):
            print(f'hourly log reduced from {ini_size} to {len(self._records)}')

    def _update_requests_rate_log(self):
        rate = str(len(self._records))
        time = dt.datetime.strftime(dt.datetime.utcnow(), TIME_FORMAT)
        with open(REQUESTS_RATE_LOG, 'a') as rate_file:
            print('\t'.join([time, rate]) + ' requests per hour', flush=True)
            print('\t'.join([time, rate]), file=rate_file, end='\n')


def monitor_logs():
    while True:
        with open(REQUESTS_LOG, 'r') as log_file:
            data = log_file.read()
        table = LogTable([LogRecord(*l.split('\t')) for l in data.splitlines()])
        table.log_requests_rate()
        print('sleeping for {:.0f} mins'.format(SLEEP_TIME / 60))
        sleep(SLEEP_TIME)


def plot_request_rate():
    import matplotlib.pyplot as plt

    with open(REQUESTS_RATE_LOG, 'r') as ratefile:
        data = ratefile.read()
    times_rates = [l.split('\t') for l in data.splitlines()]
    times = [r[0] for r in times_rates]
    rates = [int(r[1]) for r in times_rates]
    plt.bar(times, rates)
    plt.savefig(os.path.join('logs', 'requests_rate.png'))



if __name__ == '__main__':
    monitor_logs()
    # plot_request_rate()
