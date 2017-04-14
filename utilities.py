''' Utilities for football scores '''


import os
import json
from datetime import datetime


def datetime_string_make_aware(datetime_string, dt_format):
    return datetime.strptime(datetime_string, dt_format).astimezone()


def save_json(data, filename, folder='data'):
    ensure_folder_exists(folder)
    with open(os.path.join(folder, filename), 'a') as json_file:
        json.dump(data, json_file)


def load_json(filename, folder='data'):
    ensure_folder_exists(folder)
    with open(os.path.join(folder, filename)) as json_file:
        data = json.load(json_file)
    return data

def ensure_folder_exists(folder):
    if not os.path.isdir(folder):
        os.mkdir(folder)
