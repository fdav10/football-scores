'''
Module where the database and API calls are linked.
'''

from footie_scores import settings
from footie_scores.apis.football_api import FootballAPI
from footie_scores.utils.scheduling import start_periodic_calls


def start_api_calls(competitions=settings.COMPS):
    comp_api = FootballAPI()
    start_periodic_calls(45, comp_api.todays_fixtures_to_db, (competitions,))
    # start_periodic_calls(45, single_api_call, (competitions,))


def single_api_call(competitions=settings.COMPS):
    comp_api = FootballAPI()
    comp_api.todays_fixtures_to_db(competitions)


def save_competitions_to_db():
    comp_api = FootballAPI()
    comp_api.competitions_to_db()
