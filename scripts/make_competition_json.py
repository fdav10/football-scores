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
    1205: 'ELC',
    1221: 'FL1',
    1229: 'BL1',
    1232: 'GSL',
    1265: 'SB',
    1269: 'SA',
    1232: 'DED',
    1352: 'PPL',
    1397: 'CDR',
    1399: 'PD',
}

fa = FootballAPI()
fd = FootballData()


def lookup_fdata_comp_by_code(comps, comp_code):
    try:
        return next((comp for comp in comps if comp['short_name'] == comp_code))
    except StopIteration:
        return {}


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

def make_comps_json(fapi_comps, fdata_comps):
    json_comps = {'football-api_api_id_lookup': {},
                  'football-data_api_id_lookup': {}}
    for comp in fapi_comps:
        fapi_id = comp['api_id']
        fdata_comp = lookup_fdata_comp_by_code(fdata_comps, fapi_code_map.get(fapi_id, None))
        fdata_id = fdata_comp.get('football-data_api_id', None)
        json_comps['football-api_api_id_lookup'][fapi_id] = {
            'football-data_api_id': fdata_id,
            'football-api_api_name': comp['name'],
            'football-data_api_name': fdata_comp.get('name', None)}
        json_comps['football-data_api_id_lookup'][fdata_id] = {
            'football-api_api_id': fapi_id,
            'football-api_api_name': comp['name'],
            'football-data_api_name': fdata_comp.get('name', None)}

    return json_comps


def save_competition_json(comps):
    with open(os.path.join(
            'footie_scores', 'maps', 'competitions.json'), 'w') as cjson:
        cjson.write(json.dumps(comps, indent=4, ensure_ascii=False))


def main(request_data=False):
    if request_data:
        save_football_api_comps()
        save_football_data_comps()
    fapi_comps = load_football_api_comps()
    fdata_comps = load_football_data_comps()
    comps_json = make_comps_json(fapi_comps, fdata_comps)
    save_competition_json(comps_json)


if __name__ == '__main__':
    main()
