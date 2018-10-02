''' Utilities for logging functions '''


import logging
import os

from footie_scores import REPO_ROOT
from . import time


def start_logging():
    format_='%(asctime)s:' + logging.BASIC_FORMAT
    logging.basicConfig(level=logging.DEBUG,
                        # format=format_,
                        format=format_,
                        datefmt="%m-%d %H:%M:%S")
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    console.setFormatter(logging.Formatter(format_))
    logging.getLogger().addHandler(console)


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
        with open(log_file_name, 'a') as log_file:
            for url in log_urls:
                log_file.write('{}\t{}\n'.format(instance.base_url + url, time.now()))
        output = f(instance, *urls, **kwargs)
        return output
    return requests_wrapper
