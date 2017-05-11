'''
Module where the database and API calls are linked.
'''

from footie_scores import db
from footie_scores.utils.log import start_logging
from footie_scores.apis.football_api import FootballAPI
from footie_scores.utils.scheduling import start_periodic_calls

COMPETITIONS = FootballAPI().get_competitions()
FILTER_COUNTRIES = ('England', 'France', 'Germany', 'Spain', 'Italy',
                    'Portugal', 'International')
# FILTER_COUNTRIES = ('Spain',)
FILTERED_COMPETITIONS = [
    comp for comp in COMPETITIONS if comp['region'] in FILTER_COUNTRIES]
# FILTERED_COMPETITIONS = [
#     comp for comp in COMPETITIONS if comp['name'] == 'Premier League']

API_MAP = {
    'football-api': FootballAPI,
}


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
