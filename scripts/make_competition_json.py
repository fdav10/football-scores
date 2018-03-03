#!/usr/bin/env python

import os, json, logging

from footie_scores import db
from footie_scores.db import queries
from footie_scores.utils.log import start_logging
from footie_scores.apis.football_data import FootballData
from footie_scores.apis.football_api import FootballAPI

logger = logging.getLogger(__name__)

start_logging()

fapi_code_map = {
    1005: 'CL',
    1007: 'EL',
    1198: 'FAC',
    1204: 'PL',
    1205: 'EL1',
    1221: 'FL1',
    1229: 'BL1',
    1232: 'GSL',
    1265: 'SB',
    1269: 'SA',
    1232: 'DED',
    1352: 'PPL',
    1397: 'PD',
}

fa = FootballAPI()
fd = FootballData()

def save_football_api_comps():
    fa_comps = fa.get_competitions()
    with open(os.path.join(
            'footie_scores', 'maps', 'football_api_competitions.json'), 'w') as cjson:
        cjson.write(json.dumps(fa_comps, indent=4, ensure_ascii=False))

def save_football_data_comps():
    fd_comps = fd.get_competitions()
    with open(os.path.join(
            'footie_scores', 'maps', 'football_data_competitions.json'), 'w') as cjson:
        cjson.write(json.dumps(fd_comps, indent=4, ensure_ascii=False))

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

def specify_api_ids(fa_comps):
    for comp in fa_comps:
        comp['football-api_api_id'] = comp.pop('api_id')
        comp['football-data_api_id'] = None


def something_else():
    fd_comps = fd.get_competitions()
    fd_names = [comp['name'] for comp in fd_comps]

    for comp in fd_comps:
        print(comp['name'], comp['short_name'], comp['api_id'])


def save_competition_json(comps):
    with open(os.path.join(
            'footie_scores', 'maps', 'competitions.json'), 'w') as cjson:
        cjson.write(json.dumps(comps, indent=4, ensure_ascii=False))


def add_football_data_data(comps, fd_comps):
    def comp_from_code(code):
        try:
            return next((comp for comp in fd_comps if comp['short_name']==code))
        except StopIteration:
            return {}
    for comp in comps:
        fapi_id = int(comp['football-api_api_id'])
        fd_code = fapi_code_map.get(fapi_id, None)
        fd_comp = comp_from_code(fd_code)
        fd_id = fd_comp.get('api_id', None)
        n_teams = fd_comp.get('n_teams', None)
        n_fixtures = fd_comp.get('n_fixtures', None)
        comp['football-data_api_id'] = fd_id
        comp['number_of_fixtures'] = n_fixtures
        comp['number_of_teams'] = n_teams


def main():
    comps_json = load_football_api_comps()
    fdata_comps = load_football_data_comps()
    specify_api_ids(comps_json)
    add_football_data_data(comps_json, fdata_comps)
    save_competition_json(comps_json)
    

if __name__ == '__main__':
    # save_football_api_comps()
    # save_football_data_comps()
    main()
