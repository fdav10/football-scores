'''
Module where the database and API calls are linked.
'''

import os
import json

from footie_scores import db
from footie_scores.utils.log import start_logging
from footie_scores.apis.football_api import FootballAPI
from footie_scores.utils.scheduling import start_periodic_calls


def _load_competitions():
    mod_folder = os.path.split(__file__)[:-1]
    api_folder = os.path.join(*(mod_folder +('apis',)))
    with open(os.path.join(api_folder, 'football_api_competitions.json'), 'r+') as compf:
        competitions = json.load(compf)
    return competitions


COMPETITIONS = _load_competitions()
FILTER_COUNTRIES = ('England', 'France', 'Germany', 'Spain', 'Italy',
                    'Portugal', 'International')
FILTERED_COMPETITIONS = [
    comp for comp in COMPETITIONS if comp['region'] in FILTER_COUNTRIES]


def start_api_calls(competitions=FILTERED_COMPETITIONS):
    comp_api = FootballAPI()
    start_periodic_calls(45, comp_api.todays_fixtures_to_db, (competitions,))
    # start_periodic_calls(45, single_api_call, (competitions,))


def single_api_call(competitions=FILTERED_COMPETITIONS):
    comp_api = FootballAPI()
    comp_api.todays_fixtures_to_db(competitions)


def retrieve_fixtures_from_db(competitions=FILTERED_COMPETITIONS):
    fixtures = []
    for competition in competitions:
        comp_fixtures = db.interface.get_competition_fixtures_by_id(competition['id'])
        fixtures.append({
            'name': competition['name'],
            'fixtures': comp_fixtures
        })
    return fixtures


def retrieve_fixture_from_db(fixture_id):
    return db.interface.get_fixture_by_id(fixture_id)


if __name__ == '__main__':
    start_logging()
    #start_api_calls()
    single_api_call()
    retrieve_fixtures_from_db()
