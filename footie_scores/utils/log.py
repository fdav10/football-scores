''' Utilities for logging functions '''


import logging


def start_logging():
    logging.basicConfig(level=logging.DEBUG,
                        filename='logs/app.log',
                        filemode='a')

    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    console.setFormatter(logging.Formatter(logging.BASIC_FORMAT))
    logging.getLogger().addHandler(console)



def log_list(list_, logger, intro=None, prefix='', suffix=''):
    if list_:
        if intro:
            logger.info(intro)
        for i in list_:
            logger.info(prefix + i + suffix)
