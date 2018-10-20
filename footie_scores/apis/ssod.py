#!usr/bin/env python3
''' Interface to Soccer Sports Open Data API '''

import os
import logging
from datetime import date

import requests

from footie_scores.apis.base import FootballAPICaller
from footie_scores.utils.time import datetime_string_make_aware


logger = logging.getLogger(__name__)


class SoccerSportsOpenData(FootballAPICaller):
    '''
    Calls to the Soccer-Sports Open Data API

    http://api.football-data.org/v1/
    
    get prefix indicates an API call
    '''

    def __init__(self, id_league, id_season):
        raise Exception("This class deprecated because API calls are expensive when above limit of 3000/month")
        self.id_league = id_league
        self.id_season = id_season
        self.base_url = 'https://sportsop-soccer-sports-open-data-v1.p.mashape.com/v1/'
        self.headers = {
            'X-Mashape-Key': os.environ['ssod_key'],
            'Accept': 'application/json'}
        self.date_format = '%Y-%m-%dT%H:%M:%S%z'
        self.dt_format = '%Y-%m-%dT%H:%M:%S%z'
        self.match_page_ready_map = {
            'team_home': ('home', 'team'),
            'team_away': ('away', 'team'),
            'score_home': ('home', 'goals'),
            'score_away': ('away', 'goals'),
            'time_kick_off': ('TODO',),
            'time_elapsed': ('TODO',),
            }

    def _todays_fixtures(self):
        today = date.today()
        active_rounds = self._active_rounds()
        id_rounds = [round_['round_slug'] for round_ in active_rounds]

        active_fixtures = []
        for id_ in id_rounds:
            active_fixtures += self._get_matches_in_round(id_)

        todays_fixtures = [f for f in active_fixtures if f['date_match'].date() == today]
        return todays_fixtures

    def _active_rounds(self):
        ''' Return rounds which include today's date '''
        logger.info('Getting active rounds')

        today = date.today()
        rounds = self._get_rounds_in_season()
        round_dates = [[r['start_date'].date(), r['end_date'].date()] for r in rounds]
        active_rounds = [
            r for r, d in zip(rounds, round_dates) if d[0] <= today <= d[1]]

        return active_rounds

    def _get_matches_in_round(self, id_round):

        minutes_to_cache_expire = 0.1
        matches_url = 'leagues/{}/seasons/{}/rounds/{}/matches'.format(
            self.id_league, self.id_season, id_round)
        matches = self.check_cache_else_request(
            matches_url, minutes_to_cache_expire, id_round)['data']['matches']

        for match in matches:
            match.update(self._get_match_details(id_round, match['match_slug']))

        return self._make_dates_aware(matches, date_keys=('date_match',))

    def _get_match_details(self, id_round, id_match):

        minutes_to_cache_expire = 0.1
        match_url = 'leagues/{}/seasons/{}/rounds/{}/matches/{}'.format(
            self.id_league, self.id_season, id_round, id_match)
        match_details = self.check_cache_else_request(
            match_url, minutes_to_cache_expire, id_round)

        return match_details

    def _get_rounds_in_season(self):
        ''' Return all fixtures for a season. '''
        minutes_to_cache_expire = 5
        fixtures_url = 'leagues/{}/seasons/{}/rounds'.format(self.id_league, self.id_season)
        rounds = self.check_cache_else_request(
            fixtures_url, minutes_to_cache_expire, self.id_season)['data']['rounds']

        return self._make_dates_aware(rounds, date_keys=('start_date', 'end_date'))

    def _make_dates_aware(self, list_with_dates, date_keys):
        ''' Convert date-time strings into Python datetime objects '''

        for dict_ in list_with_dates:
            for key in date_keys:
                date = dict_[key]
                dict_[key] = datetime_string_make_aware(date, self.dt_format)

        return list_with_dates

if __name__ == '__main__':
    start_logging()
