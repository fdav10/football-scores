''' Utilities for logging functions '''


import logging
import os
import datetime as dt

from footie_scores import REPO_ROOT
from . import time


TIME_FORMAT =  "%Y-%m-%d %H:%M:%S"


def start_logging():
    format_='%(asctime)s:' + logging.BASIC_FORMAT
    logging.basicConfig(level=logging.DEBUG,
                        format=format_,
                        datefmt="%m-%d %H:%M:%S")
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)


def log_list(list_, logger, intro=None, template='%s'):
    if list_:
        if intro:
            logger.info(intro)
        for i in list_:
            logger.info(template, i)


def log_request(f, *args, **kwargs):
    log_file_name = os.path.join(REPO_ROOT, 'logs', 'hourly_requests.log')
    def requests_wrapper(instance, *urls, **kwargs):
        log_urls = (urls,) if not isinstance(urls, (list, tuple)) else urls
        time_now = dt.datetime.strftime(time.now(), "%Y-%m-%d %H:%M:%S")
        with open(log_file_name, 'a') as log_file:
            for url in log_urls:
                log_file.write('{}\t{}\n'.format(instance.base_url + url, time_now))
        output = f(instance, *urls, **kwargs)
        return output
    return requests_wrapper
