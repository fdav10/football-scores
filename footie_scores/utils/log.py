''' Utilities for logging functions '''


import sys
import logging


logger = logging.getLogger(__name__)


def start_logging():
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)


def log_list(list_, intro=None):
    if list_:
        if intro:
            logger.info(intro)
        for i in list_:
            logger.info(i)
