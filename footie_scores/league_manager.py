''' '''

from datetime import date
from collections import defaultdict

from flask import Flask, render_template

#from footie_scores.app import run
from footie_scores.utils.cache import load_json
from footie_scores.utils.log import start_logging
from footie_scores.apis.football_api import FootballAPI
from footie_scores.utils.scheduling import start_periodic_calls

COMPETITIONS = FootballAPI()._get_competitions()['data']
FILTER_COUNTRIES = (
    'England', 'France', 'Germany', 'Spain', 'Italy', 'Portugal',
    'International')
FILTERED_COMPETITIONS = [
    comp for comp in COMPETITIONS if comp['region'] in FILTER_COUNTRIES]


def start_api_calls(competitions=FILTERED_COMPETITIONS):
    comp_api = FootballAPI()
    start_periodic_calls(45, comp_api.page_ready_todays_fixtures_to_db, (competitions,))


def single_api_call(competitions=FILTERED_COMPETITIONS):
    comp_api = FootballAPI()
    comp_api.page_ready_todays_fixtures_to_db(competitions)


def retrieve_fixtures_from_cache(competitions=FILTERED_COMPETITIONS):
    fixtures = []
    for competition in competitions:
        try:
            comp_fixtures = load_json('todays_fixtures_' + competition['id'])
        except FileNotFoundError:
            comp_fixtures = []

        fixtures.append({
            'name': competition['name'],
            'fixtures': comp_fixtures
        })

    return fixtures


def retrieve_fixture_from_cache(fixture_id):
    fixture = load_json('fixture_' + fixture_id)
    return fixture


if __name__ == '__main__':
    start_logging()
    start_api_calls()
