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

#COMPETITIONS = [
#    {'api_name': 'champions league', 'print_name': 'Champions League'},
#    {'api_name': 'europa league', 'print_name': 'Europa League'},
#    {'api_name': 'england cup', 'print_name': 'FA Cup'},
#    {'api_name': 'england', 'print_name': 'Premier League'},
#    {'api_name': 'france', 'print_name': 'Ligue 1'},
#    {'api_name': 'germany', 'print_name': 'Bundesliga'},
#    {'api_name': 'italy', 'print_name': 'Serie A'},
#    {'api_name': 'portugal', 'print_name': 'Primeira Liga'},
#    {'api_name': 'spain', 'print_name': 'La Liga'},
#    {'api_name': 'austria', 'print_name': },
#    {'api_name': 'belgium', 'print_name': },
#    {'api_name': 'czechoslovakia', 'print_name': },
#    {'api_name': 'england league cup', 'print_name': },
#    {'api_name': 'england 2nd', 'print_name': },
#    {'api_name': 'greece', 'print_name': },
#    {'api_name': 'italy', 'print_name': },
#    {'api_name': 'netherlands', 'print_name': },
#    {'api_name': 'spain cup', 'print_name': },
#    {'api_name': 'switzerland', 'print_name': },
#    {'api_name': 'turkey', 'print_name': },
#    {'api_name': 'ukraine', 'print_name': },
#    {'api_name': 'russia', 'print_name': }
#]


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
            comp_fixtures = load_json('todays_fixtures_' + competition['api_name'])
        except FileNotFoundError:
            comp_fixtures = []

        fixtures.append({
            'name': competition['print_name'],
            'fixtures': comp_fixtures
        })

    return fixtures


if __name__ == '__main__':
    start_logging()
    start_api_calls()
