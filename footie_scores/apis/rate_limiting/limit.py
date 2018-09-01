

import os
from collections import namedtuple

from footie_scores import REPO_ROOT

LogRecord = namedtuple('LogRecord', ['url', 'time'])


class LogTable(list):
    def __init__(self, items):
        super(LogTable, self).__init__(items)

    def purge_old_records(self, minutes):
        pass


def convert_log_to_table():
    with open(os.path.join(REPO_ROOT, 'logs', 'hourly_requests.log'), 'r') as log_file:
        data = log_file.read()
    table = [LogRecord(*l.split('\t')) for l in data.splitlines()]
    import ipdb; ipdb.set_trace()


def log_request(f, *args, **kwargs):
    log_file_name = os.path.join(REPO_ROOT, 'logs', 'hourly_requests.log')
    def requests_wrapper(instance, *urls, **kwargs):
        log_urls = (urls,) if not isinstance(urls, (list, tuple)) else urls
        with open(log_file_name, 'a') as log_file:
            for url in log_urls:
                log_file.write('{}\t{}\n'.format(instance.base_url + url, utils.time.now()))
        output = f(instance, *urls, **kwargs)
        return output
    return requests_wrapper


if __name__ == '__main__':
    convert_log_to_table()
