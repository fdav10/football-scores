#!usr/bin/env python3
''' Interfaces to football score APIs '''

import os
import logging
from datetime import date

import requests

from footie_scores.utils.log import start_logging
from footie_scores.apis.base import FootballAPICaller


logger = logging.getLogger(__name__)



class FootballAPI(FootballAPICaller):
    '''
    Calls to the Football-API API

    https://football-api.com/
    '''

    def __init__(self, id_league='1204', id_season=''):
        self.id_league = id_league
        self.id_season = id_season
        self.base_url = 'http://api.football-api.com/2.0/'
        self.headers = None
        self.key = os.environ['football_api_key']
        self.url_suffix = 'Authorization=' + self.key
        self.date_format = '%d.%m.%Y'
        self.match_page_ready_map = {
            'team_home': 'localteam_name',
            'team_away': 'visitorteam_name',
            'score_home': 'localteam_score',
            'score_away': 'visitorteam_score',
            'time_kick_off': 'time',
            'time_elapsed': 'timer',
        }

    def _get_competitions(self):
        minutes_to_cache_expiry = 60 * 24
        competitions_url = 'competitions?'
        return self.check_cache_else_request(
            competitions_url,
            minutes_to_cache_expiry,
        )

    def _get_fixtures_for_date(self, date_):
        minutes_to_cache_expiry = 0.2
        today = date_.strftime(self.date_format)
        fixtures_url = 'matches?comp_id={}&match_date={}&'.format(
            self.id_league, today)
        todays_fixtures = self.check_cache_else_request(
            fixtures_url,
            minutes_to_cache_expiry,
        )['data']

        return self._this_league_only(self.id_league, todays_fixtures)

    def _get_active_fixtures(self):
        minutes_to_cache_expiry = 0.2
        fixtures_url = 'matches?'
        active_fixtures = self.check_cache_else_request(
            fixtures_url,
            minutes_to_cache_expiry,
        )['data']

        return self._this_league_only(self.id_league, active_fixtures)

    def _this_league_only(self, league_id, matches):
        return [m for m in matches if m['comp_id'] == league_id]

    def _is_valid_response(self, response):
        try:
            assert isinstance(response, dict) and response['status'] == 'error'
            return False
        except (AssertionError, KeyError):
            return True


if __name__ == '__main__':
    start_logging()
    PL = FootballAPI()
    print (PL.page_ready_todays_fixtures())
    import ipdb; ipdb.set_trace()
