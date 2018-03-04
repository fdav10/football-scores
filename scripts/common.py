import json, os

from footie_scores.apis.football_data import FootballData
from footie_scores.apis.football_api import FootballAPI


def load_football_api_comps():
    with open(os.path.join(
            'footie_scores', 'maps', 'football_api_competitions.json'), 'r') as cjson:
        fa_comps = json.loads(cjson.read())
    return fa_comps


def load_football_data_comps():
    with open(os.path.join(
            'footie_scores', 'maps', 'football_data_competitions.json'), 'r') as cjson:
        fd_comps = json.loads(cjson.read())
    return fd_comps


def api_get_football_api_comps():
    fa = FootballAPI()
    return fa.get_competitions()


def api_get_football_data_comps():
    fd = FootballData()
    return fd.get_competitions()
