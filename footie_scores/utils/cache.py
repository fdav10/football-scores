''' Utilities for caching json objects'''

import os
import json
import logging

from footie_scores.utils.time import stime_from_now, json_expiry_as_datime, time_elapsed_from


logger = logging.getLogger(__name__)


def purge_cache_of_expired_before_load(load_func):
    def purge_cache_and_run(filename, folder='data'):
        data = load_func(filename, folder)
        expiry = json_expiry_as_datime(data)
        elapsed = time_elapsed_from(expiry)
        if elapsed.total_seconds() <= 0:
            logger.info('%s cache expired %f seconds ago' %(
                filename, abs(elapsed.total_seconds())))
            remove_from_cache(filename, folder)
            raise FileNotFoundError
        return data
    return purge_cache_and_run


def add_expiry_to_json(save_func):
    def expiry_wrapper(data, filename, cache_expiry):
        expiry_time = stime_from_now(cache_expiry)
        expiry = {'expiry_time': expiry_time}
        data.update(expiry)
        return save_func(data, filename, cache_expiry)
    return expiry_wrapper


@add_expiry_to_json
def save_json(data, filename, cache_expiry, folder='data'):
    ensure_folder_exists(folder)
    with open(os.path.join(folder, filename), 'a') as json_file:
        json.dump(data, json_file)
        logger.info('%s added to cache' %filename)


@purge_cache_of_expired_before_load
def load_json(filename, folder='data'):
    ensure_folder_exists(folder)
    with open(os.path.join(folder, filename)) as json_file:
        data = json.load(json_file)
        logger.info('%s retreived from cache' %filename)
    return data


def ensure_folder_exists(folder):
    if not os.path.isdir(folder):
        os.mkdir(folder)

def remove_from_cache(filename, folder='data'):
    os.remove(os.path.join(folder, filename))
    logger.info('Cache file deleted {}'.format(filename))
