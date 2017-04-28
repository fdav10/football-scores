''' '''

from datetime import date
from collections import defaultdict

from flask import Flask, render_template

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
    for competition in competitions:
        comp_api = FootballAPI(competition)
        start_periodic_calls(30, comp_api._todays_fixtures_to_db)


def todays_fixtures():
    # TODO move this so that this module is generic
    fapi = FootballAPI('france')
    fapi._todays_fixtures_to_db()


def competition_fixtures(competitions):
    fixtures = []
    for competition in competitions:
        comp_api = FootballAPI(competition['api_name'])
        try:
            comp_fixtures = comp_api.page_ready_todays_fixtures()
        except:
            # TODO catch custom error for no fixtures available
            comp_fixtures = []
        fixtures.append({
            'name': competition['print_name'],
            'fixtures': comp_fixtures
        })
    return fixtures

if __name__ == '__main__':
    start_logging()
    start_api_calls(('germany', 'france'))
