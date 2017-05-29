''' Utilities for logging functions '''


import sys
import logging
import datetime as dt

from footie_scores.utils.time import chop_microseconds


logger = logging.getLogger(__name__)


def start_logging():
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)


def log_list(list_, intro=None):
    if list_:
        if intro:
            logger.info(intro)
        for i in list_:
            logger.info(i)

def log_time_util_next_fixture(tdelta, sleeptime):
    logger.info('Next game in: %s', chop_microseconds(dt.timedelta(seconds=tdelta)))
    logger.info('Sleeping for: %s', chop_microseconds(dt.timedelta(seconds=sleeptime)))
