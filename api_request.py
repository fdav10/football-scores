''' just try and get a response'''

import json
from datetime import date

import requests

from utilities import fixture_date

BASE_URL = 'http://api.football-data.org/v1/'
APIKEY = '8d476a94d095407b93c0b26732a6216f'
HEADERS = {'X-Auth-Token': APIKEY}
URL = 'soccerseasons/{id}/leagueTable'.format(id=426)


def current_standings():
    request = requests.get(BASE_URL+URL, headers=HEADERS)
    return request


def get_live_scores():
    live_scores_url = 'http://soccer-cli.appspot.com/'
    request = requests.get(live_scores_url)
    return request


def get_season_fixtures():
    fixtures_url = 'competitions/{id}/fixtures'.format(id=426)
    request = requests.get(BASE_URL+fixtures_url, headers=HEADERS)
    fixtures = request.json()['fixtures']
    return fixtures


def get_todays_fixtures():
    ''' Return json encoded list of today's fixtures '''

    today = date.today()
    fixtures = get_season_fixtures()
    dates = [fixture_date(fix) for fix in fixtures]
    todays_fixtures = [f for f, date in zip(fixtures, dates) if date == today]

    return todays_fixtures


if __name__ == '__main__':
    pass
