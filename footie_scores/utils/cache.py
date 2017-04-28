''' Utilities for caching json objects'''

import os
import json
import logging

from footie_scores.utils.time import stime_from_now, json_expiry_as_datime, time_elapsed_from


FAR_IN_FUTURE = 525600 # one year in minutes


logger = logging.getLogger(__name__)


def save_json(data, filename, cache_expiry=FAR_IN_FUTURE, folder='data'):
    ensure_folder_exists(folder)
    with open(os.path.join(folder, filename), 'w') as json_file:
        json.dump(data, json_file)
        logger.info('%s added to cache' %filename)


def load_json(filename, folder='data'):
    ensure_folder_exists(folder)
    with open(os.path.join(folder, filename)) as json_file:
        data = json.load(json_file)
    return data


def ensure_folder_exists(folder):
    if not os.path.isdir(folder):
        os.mkdir(folder)


def remove_from_cache(filename, folder='data'):
    os.remove(os.path.join(folder, filename))
    logger.info('%s cache file deleted ' %filename)


def embed_in_dict_if_not_dict(data, key):
    try:
        assert type(data) is dict
    except AssertionError:
        data = {key: data}
    return data
