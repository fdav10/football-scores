''' '''

from datetime import date
from collections import defaultdict

from flask import Flask, render_template

from footie_scores.app import run
from footie_scores.utils.cache import load_json
from footie_scores.utils.log import start_logging
from footie_scores.apis.football_api import FootballAPI
from footie_scores.utils.scheduling import start_periodic_calls

AVAILABLE_COMPETITIONS = set((
    'champions league',
    'europa league',
    'austria',
    'belgium',
    'czechoslovakia',
    'england cup',
    'england league cup',
    'england',
    'england 2nd',
    'france',
    'germany',
    'greece',
    'italy 2nd',
    'italy',
    'netherlands',
    'portugal',
    'spain cup',
    'spain',
    'switzerland',
    'turkey',
    'ukraine',
    'russia',
    ))


def start_api_calls(competitions):
    comp_api_names = [c['api_name'] for c in competitions]
    comp_api = FootballAPI()
    start_periodic_calls(30, comp_api.page_ready_todays_fixtures_to_db, (comp_api_names,))


def retrieve_fixtures_from_cache(competitions):
    fixtures = []
    for competition in competitions:
        try:
            comp_fixtures = load_json('todays_fixtures_' + competition['api_name'])
        except FileNotFoundError:
            comp_fixtures = []

        fixtures.append({
            'name': competition['print_name'],
            'fixtures': comp_fixtures
        })

    return fixtures


def competition_fixtures(competitions):
    fixtures = []
    for competition in competitions:
        comp_api = FootballAPI(competition['api_name'])
        try:
            comp_fixtures = comp_api.page_ready_todays_fixtures()
        except:
            import traceback; traceback.print_exc();
            # TODO catch custom error for no fixtures available
            comp_fixtures = []
        fixtures.append({
            'name': competition['print_name'],
            'fixtures': comp_fixtures
        })
    return fixtures

if __name__ == '__main__':
    start_logging()

    start_api_calls(run.COMPETITIONS)
