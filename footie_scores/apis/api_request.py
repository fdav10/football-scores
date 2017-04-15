#!usr/bin/env python3
''' Interfaces to football score APIs '''

import os
import logging
from datetime import date, datetime, timedelta

import requests

from utils.log import start_logging
from utils.cache import save_json, load_json
from utils.time import datetime_string_make_aware


logger = logging.getLogger(__name__)


class FootballData():
    '''
    Calls to the football-data API

    http://api.football-data.org/index
    '''

    def __init__(self):
        self.base_url = 'http://api.football-data.org/v1/'
        self.headers = {'X-Auth-Token': os.environ['football_data_key']}
        self.dt_format = "%Y-%m-%dT%H:%M:%SZ"

    def get_season_fixtures(self, season_id=426):
        '''
        Return all fixtures for a season. This is an expensive
        call so don't do often
        '''
        fixtures_url = 'competitions/{id}/fixtures'.format(id=season_id)
        request = requests.get(self.base_url+fixtures_url, headers=self.headers)
        fixtures = request.json()['fixtures']
        return fixtures

    def get_todays_fixtures(self):
        ''' Return list of today's fixtures '''
        today = date.today()
        fixtures = self.get_season_fixtures()
        dates = [self._fixture_date(fix) for fix in fixtures]
        todays_fixtures = [f for f, date_ in zip(fixtures, dates) if date_ == today]
        return todays_fixtures

    def _fixture_datetime(self, fixture):
        ''' datetime.datetime object for fixture '''
        raw = fixture['date']
        return datetime.strptime(raw, self.dt_format)

    def _fixture_date(self, fixture):
        ''' datetime.date object for fixture '''
        f_datetime = self._fixture_datetime(fixture)
        return f_datetime.date()


class SoccerSportsOpenData():
    '''
    Calls to the Soccer-Sports Open Data API

    http://api.football-data.org/v1/
    
    get prefix indicates an API call
    '''

    def __init__(self, id_league, id_season):
        self.id_league = id_league
        self.id_season = id_season
        self.base_url = 'https://sportsop-soccer-sports-open-data-v1.p.mashape.com/v1/'
        self.headers = {
            'X-Mashape-Key': os.environ['ssod_key'],
            'Accept': 'application/json'}
        self.dt_format = '%Y-%m-%dT%H:%M:%S%z'

    def check_cache_else_request(self, url, cache_expiry=0, description=None):
        try:
            local_request = load_json(url.replace('/', '_')+'.json')
            return local_request
        except FileNotFoundError:
            request = requests.get(self.base_url+url, headers=self.headers).json()
            save_json(request, url.replace('/', '_')+'.json', cache_expiry)
            return request

    def _todays_fixtures(self):
        today = date.today()
        today = date(2017, 4, 8)
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
        today = date(2017, 4, 8)
        rounds = self._get_rounds_in_season()
        round_dates = [[r['start_date'].date(), r['end_date'].date()] for r in rounds]
        active_rounds = [
            r for r, d in zip(rounds, round_dates) if d[0] <= today <= d[1]]

        return active_rounds

    def _get_matches_in_round(self, id_round):
        minutes_to_cache_expire = 0.5
        matches_url = 'leagues/{}/seasons/{}/rounds/{}/matches'.format(
            self.id_league, self.id_season, id_round)

        matches = self.check_cache_else_request(
            matches_url, minutes_to_cache_expire, id_round)['data']['matches']
        return self._make_dates_aware(matches, date_keys=('date_match',))

    def _get_rounds_in_season(self):
        ''' Return all fixtures for a season. '''
        minutes_to_cache_expire = 5
        fixtures_url = 'leagues/{}/seasons/{}/rounds'.format(self.id_league, self.id_season)
        rounds = self.check_cache_else_request(
            fixtures_url, minutes_to_cache_expire, self.id_season)['data']['rounds']

        return self._make_dates_aware(rounds, date_keys=('start_date', 'end_date'))

    def todays_fixtures_page_ready(self):
        todays_fixtures = []
        logger.info('Today\'s fixtures requested')
        for fixture in self._todays_fixtures():
            todays_fixtures.append({
                'team_home': fixture['home']['team'],
                'team_away': fixture['away']['team'],
                'score_home': fixture['home']['goals'],
                'score_away': fixture['away']['goals'],
                'time_kick_off': '15:00',
                'time_elapsed': '90',
            })
        logger.info('Today\'s fixtures retrieved')
        return todays_fixtures

    def _make_dates_aware(self, list_with_dates, date_keys):
        ''' Convert date-time strings into Python datetime objects '''

        for dict_ in list_with_dates:
            for key in date_keys:
                date = dict_[key]
                dict_[key] = datetime_string_make_aware(date, self.dt_format)

        return list_with_dates


if __name__ == '__main__':
    start_logging()

    sssod = SoccerSportsOpenData(id_league='premier-league', id_season='16-17')
    sssod.todays_fixtures_page_ready()
