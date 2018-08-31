''' Utilities for logging functions '''


import sys
import logging


def start_logging():
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)


def log_list(list_, logger, intro=None):
    if list_:
        if intro:
            logger.info(intro)
        for i in list_:
            logger.info(i)
