'''
Module where the database and API calls are linked.
'''

#from footie_scores.app import run
from footie_scores.utils.cache import load_json
from footie_scores.utils.log import start_logging
from footie_scores.apis.football_api import FootballAPI
from footie_scores.utils.scheduling import start_periodic_calls
from footie_scores import db

COMPETITIONS = FootballAPI().get_competitions()['data']
FILTER_COUNTRIES = ('England', 'France', 'Germany', 'Spain', 'Italy',
                    'Portugal', 'International')
FILTER_COUNTRIES = ('Spain',)
# FILTERED_COMPETITIONS = [
#     comp for comp in COMPETITIONS if comp['region'] in FILTER_COUNTRIES]
FILTERED_COMPETITIONS = [
    comp for comp in COMPETITIONS if comp['name'] == 'Premier League']

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


def retrieve_fixtures_from_db(competitions=FILTERED_COMPETITIONS):
    fixtures = []
    for competition in competitions:
        comp_fixtures = db.interface.get_competition_fixtures_by_id(competition['id'])
        pr_comp_fixtures = make_fixtures_page_ready(comp_fixtures)
        fixtures.append({
            'name': competition['name'],
            'fixtures': pr_comp_fixtures
        })

    return fixtures


def make_fixtures_page_ready(fixtures):
    pr_fixtures = []
    for fixture in fixtures:
        source_api = API_MAP[fixture.api_source]
        page_ready_fixture = source_api.make_fixture_page_ready(fixture.data)
        pr_fixtures.append(page_ready_fixture)
    return pr_fixtures


def retrieve_fixture_from_db(fixture_id):
    fixture = load_json('fixture_' + fixture_id)
    return fixture


if __name__ == '__main__':
    start_logging()
    #start_api_calls()
    single_api_call()
    retrieve_fixtures_from_db()
