''' Utilities for logging functions '''


import sys
import logging


logger = logging.getLogger(__name__)


def start_logging():
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
